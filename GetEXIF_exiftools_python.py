import os
import csv
import subprocess
import json
import platform
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

try:
    import pillow_heif
except ImportError:
    pillow_heif = None
    print("Warning: pillow-heif not installed. HEIC/HEIF metadata fallback may be limited.")

# r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 1 - NIOA'
# r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 2 - Benalla'
# r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 3 - Mulwala'
# r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 4 - Mulwala'
root_dir = r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 5 - Mulwala'
# root_dir = r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos'
# root_dir = r'C:\C_working\TS19_working\Fullsize\TEST'
output_csv = r'C:\C_working\TS19_working\PhotoEXIFInfo_T5_Mulwala.csv'
valid_extensions = {'.jpg', '.jpeg', '.heif', '.heic', '.png', '.mov'}

def run_exiftool(file_path):
    try:
        cmd = ['exiftool', '-j', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata_list = json.loads(result.stdout)
        if metadata_list:
            return metadata_list[0]
        return {}
    except Exception as e:
        return {'Error': str(e)}

def parse_exif_date_str(date_str):
    formats = [
        '%Y:%m:%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%Y:%m:%d',
    ]

    date_str_clean = date_str.strip()
    if '.' in date_str_clean:
        date_str_clean = date_str_clean.split('.')[0]
    if date_str_clean.endswith('Z'):
        date_str_clean = date_str_clean[:-1]

    for fmt in formats:
        try:
            return datetime.strptime(date_str_clean, fmt)
        except Exception:
            pass
    return None

def format_datetime(dt):
    if dt is None:
        return None
    day_format = '%-d' if platform.system() != 'Windows' else '%#d'
    return dt.strftime(f'{day_format}/%m/%Y %H:%M:%S')

def parse_dates(metadata):
    date_tags = [
        'DateTimeOriginal', 'CreateDate', 'ModifyDate',
        'MediaCreateDate', 'TrackCreateDate', 'DateCreated',
        'DateTimeDigitized', 'FileModifyDate', 'FileCreateDate',
        'CreationDate', 'ContentCreateDate', 'DateCreated'
    ]

    dates = {}
    for tag in date_tags:
        val = metadata.get(tag)
        if val:
            dt = parse_exif_date_str(val)
            if dt:
                dates[tag] = dt
    return dates

def extract_device_info(metadata):
    device_id = metadata.get('ImageUniqueID') or metadata.get('UniqueCameraModel') or None
    make = metadata.get('Make') or None
    model = metadata.get('Model') or None
    serial_number = metadata.get('SerialNumber') or metadata.get('CameraSerialNumber') or None
    return device_id, make, model, serial_number

def extract_metadata_pillow(file_path, ext):
    """
    Fallback method to extract metadata using Pillow and pillow-heif.
    Returns a dictionary similar to exiftool output but with limited info.
    """
    metadata = {}
    try:
        if ext in {'.heic', '.heif'}:
            if not pillow_heif:
                metadata['Error'] = "pillow_heif not installed"
                return metadata
            heif_file = pillow_heif.read_heif(file_path)
            image = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride
            )
            exif = image.getexif()
        else:
            image = Image.open(file_path)
            exif = image._getexif()

        if exif:
            for tag, val in exif.items():
                tag_name = TAGS.get(tag, tag)
                metadata[tag_name] = val

            # Pillow-extracted dates are often string, reformat if possible
            # e.g. DateTimeOriginal may be 'YYYY:MM:DD HH:MM:SS'
        else:
            metadata['Error'] = 'No EXIF data found'
    except Exception as e:
        metadata['Error'] = str(e)
    return metadata

def extract_mov_creation_date_ffprobe(file_path):
    """
    Fallback for .mov files using ffprobe to extract creation_time.
    """
    metadata = {}
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-print_format', 'json', '-show_entries',
            'format_tags=creation_time', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        ffprobe_data = json.loads(result.stdout)
        tags = ffprobe_data.get('format', {}).get('tags', {})
        if 'creation_time' in tags:
            metadata['CreateDate'] = tags['creation_time']
    except Exception as e:
        metadata['Error'] = str(e)
    return metadata

def main():
    csv_fields = [
        'file',  # filename only
        'extension',  # file extension
        'file_path',
        'exif_accessible',
        'date_times',
        'earliest_date',
        'device_id',
        'make',
        'model',
        'serial_number'
    ]
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
        writer.writeheader()

        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in valid_extensions:
                    continue

                file_path = os.path.join(dirpath, filename)

                exif_accessible = 'No'
                dates = {}
                device_id = None
                make = None
                model = None
                serial_number = None

                # TRY ExifTool first
                metadata = run_exiftool(file_path)

                if 'Error' in metadata:
                    # FALLBACKS

                    # For images (JPG, PNG, HEIC)
                    if ext in {'.jpg', '.jpeg', '.png', '.heic', '.heif'}:
                        metadata = extract_metadata_pillow(file_path, ext)

                    # For MOV videos
                    elif ext == '.mov':
                        metadata = extract_mov_creation_date_ffprobe(file_path)

                if 'Error' not in metadata:
                    exif_accessible = 'Yes'
                    dates = parse_dates(metadata)
                    device_id, make, model, serial_number = extract_device_info(metadata)

                earliest_date = min(dates.values()) if dates else None

                writer.writerow({
                    'file': filename,
                    'extension': ext,
                    'file_path': file_path,
                    'exif_accessible': exif_accessible,
                    'date_times': json.dumps({k: v.isoformat() for k, v in dates.items()}, ensure_ascii=False),
                    'earliest_date': format_datetime(earliest_date),
                    'device_id': device_id,
                    'make': make,
                    'model': model,
                    'serial_number': serial_number
                })
                output_txt = file_path[143:]

                print(f"Processed: {output_txt}")

    print("Hybrid metadata extraction completed.")

if __name__ == '__main__':
    main()
