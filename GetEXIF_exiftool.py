import os
import csv
import subprocess
import json
import platform
from datetime import datetime

# Root directory containing your files
root_dir = r'C:\C_working\TS19_working\Resized'

# Output CSV file path
output_csv = r'C:\C_working\TS19_working\PhotoEXIFInfo.csv'

# File extensions to process
valid_extensions = {'.jpg', '.jpeg', '.heif', '.heic', '.png', '.mov'}

def run_exiftool(file_path):
    """
    Runs exiftool on the given file and returns metadata as a dictionary.
    """
    try:
        # -j outputs JSON, -n disables print conversion for numerical tags (if desired)
        cmd = ['exiftool', '-j', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata_list = json.loads(result.stdout)
        if metadata_list:
            return metadata_list[0]
        else:
            return {}
    except Exception as e:
        return {'Error': str(e)}

def parse_dates(metadata):
    """
    Extract and parse all date fields found in metadata, returning a dict of date_name: datetime.
    """
    # Common date tag names in ExifTool output (extend as needed)
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

def parse_exif_date_str(date_str):
    """
    Parse date string formats from ExifTool output to a Python datetime object.
    Handles various common ExifTool date/time formats.
    """
    # Example formats ExifTool generally outputs:
    formats = [
        '%Y:%m:%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%Y:%m:%d',
    ]

    # Sometimes values have fractional seconds or timezone 'Z', strip these if needed
    date_str_clean = date_str.strip()
    # Remove fractional seconds (e.g. 2025:05:07 08:18:53.123)
    if '.' in date_str_clean:
        date_str_clean = date_str_clean.split('.')[0]
    # Remove trailing 'Z' (Zulu/UTC)
    if date_str_clean.endswith('Z'):
        date_str_clean = date_str_clean[:-1]

    for fmt in formats:
        try:
            return datetime.strptime(date_str_clean, fmt)
        except Exception:
            continue
    return None

def format_datetime(dt):
    """
    Format datetime object as d/mm/yyyy h:mm:ss or return None if dt is None.
    Handles Windows and non-Windows platforms for day formatting.
    """
    if dt is None:
        return None
    day_format = '%-d' if platform.system() != 'Windows' else '%#d'
    return dt.strftime(f'{day_format}/%m/%Y %H:%M:%S')

def extract_device_info(metadata):
    """
    Extract device info fields from metadata dictionary.
    """
    device_id = metadata.get('ImageUniqueID') or metadata.get('UniqueCameraModel') or None
    make = metadata.get('Make') or None
    model = metadata.get('Model') or None
    serial_number = metadata.get('SerialNumber') or metadata.get('CameraSerialNumber') or None

    return device_id, make, model, serial_number

def main():
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
                if ext in valid_extensions:
                    file_path = os.path.join(dirpath, filename)
                    exif_accessible = 'No'
                    dates = {}
                    device_id = None
                    make = None
                    model = None
                    serial_number = None

                    metadata = run_exiftool(file_path)

                    if 'Error' not in metadata:
                        exif_accessible = 'Yes'
                        dates = parse_dates(metadata)
                        device_id, make, model, serial_number = extract_device_info(metadata)

                    earliest_date = min(dates.values()) if dates else None

                    writer.writerow({
                        'file_path': file_path,
                        'exif_accessible': exif_accessible,
                        'date_times': json.dumps({k: v.isoformat() for k, v in dates.items()}, ensure_ascii=False),
                        'earliest_date': format_datetime(earliest_date),
                        'device_id': device_id,
                        'make': make,
                        'model': model,
                        'serial_number': serial_number
                    })

                    print(f"Processed: {file_path}")

    print("Metadata extraction with ExifTool completed.")

if __name__ == '__main__':
    main()
