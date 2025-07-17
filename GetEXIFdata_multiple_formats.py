import os
import csv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import pillow_heif
import subprocess
import json

# Root directory containing your files
root_dir = r'C:\C_working\TS19_working\Fullsize\TEST'

# Output CSV path
output_csv = r'C:\C_working\TS19_working\PhotoEXIFInfo.csv'

# File extensions to process
image_extensions = {'.jpg', '.jpeg', '.heif', '.heic', '.png'}
video_extensions = {'.mov'}

def extract_exif_from_image(image_path):
    exif_data = {}
    try:
        ext = os.path.splitext(image_path)[1].lower()
        if ext in {'.heif', '.heic'}:
            heif_file = pillow_heif.read_heif(image_path)
            image = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride
            )
            exif = image.getexif()
        else:
            image = Image.open(image_path)
            exif = image._getexif()

        if exif is not None:
            for tag, value in exif.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
    except Exception as e:
        exif_data['Error'] = str(e)
    return exif_data

def extract_metadata_from_png(image_path):
    # PNG does not have standard EXIF; extract date from tEXt chunks if available
    metadata = {}
    try:
        image = Image.open(image_path)
        info = image.info
        # Sometimes dates might be in 'date:create' or 'Creation Time' keys, check common ones
        for key in ['date:create', 'Creation Time', 'creation_time']:
            if key in info:
                metadata[key] = info[key]
    except Exception as e:
        metadata['Error'] = str(e)
    return metadata

def extract_metadata_from_mov(file_path):
    # Use ffprobe (part of ffmpeg) to extract metadata from MOV file
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
            metadata['creation_time'] = tags['creation_time']
    except Exception as e:
        metadata['Error'] = str(e)
    return metadata

def parse_date(date_str):
    # Try multiple date formats that might appear in metadata
    formats = [
        '%Y:%m:%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f%z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue
    return None

def gather_dates(exif_or_meta):
    # Potential date keys to check, extend as needed
    date_keys = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime', 'creation_time', 'date:create', 'Creation Time']
    dates = {}
    for key in date_keys:
        date_str = exif_or_meta.get(key)
        if date_str:
            parsed = parse_date(date_str)
            if parsed:
                dates[key] = parsed
    return dates

# Prepare CSV headers
csv_fields = [
    'file_path',
    'exif_accessible',
    'date_times',   # JSON string of all extracted dates as ISO strings
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
            if ext in image_extensions.union(video_extensions):
                file_path = os.path.join(dirpath, filename)
                exif_accessible = 'No'
                dates = {}
                device_id = None
                make = None
                model = None
                serial_number = None

                if ext in image_extensions:
                    if ext in {'.png'}:
                        meta = extract_metadata_from_png(file_path)
                    else:
                        meta = extract_exif_from_image(file_path)

                    if 'Error' not in meta:
                        exif_accessible = 'Yes'
                        dates = gather_dates(meta)
                        device_id = meta.get('ImageUniqueID')
                        make = meta.get('Make')
                        model = meta.get('Model')
                        serial_number = meta.get('SerialNumber')
                    else:
                        # Error extracting EXIF
                        exif_accessible = 'No'

                elif ext in video_extensions:
                    meta = extract_metadata_from_mov(file_path)
                    if 'Error' not in meta:
                        exif_accessible = 'Yes'
                        dates = gather_dates(meta)

                # Determine earliest date (if any)
                earliest_date = min(dates.values()) if dates else None

                writer.writerow({
                    'file_path': file_path,
                    'exif_accessible': exif_accessible,
                    'date_times': {k: v.isoformat() for k, v in dates.items()},
                    'earliest_date': earliest_date.isoformat() if earliest_date else None,
                    'device_id': device_id,
                    'make': make,
                    'model': model,
                    'serial_number': serial_number
                })
                print(f"Processed: {file_path}")

print("Extraction to CSV completed.")
