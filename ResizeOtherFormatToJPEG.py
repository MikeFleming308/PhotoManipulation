import os
import traceback
import csv
from datetime import datetime
from PIL import Image, ExifTags, UnidentifiedImageError
import pillow_heif
from moviepy.editor import VideoFileClip

print("import completed")

# User configuration
input_dir = r'C:\Users\mikef\OneDrive\Documents\Coding\Python\Data'
output_dir = r'C:\Users\mikef\OneDrive\Documents\Coding\Python\Output'
target_size_kb = 500
count = 0

error_log_file = os.path.join(output_dir, 'conversion_error_log.csv')
timestamp_log_file = os.path.join(output_dir, 'capture_timestamp_log.csv')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def get_capture_datetime(img):
    try:
        exif_data = img.getexif()
    except AttributeError:
        return None, None
    if not exif_data:
        return None, None

    timestamp_tags = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
    for tag, value in exif_data.items():
        decoded = ExifTags.TAGS.get(tag, tag)
        if decoded in timestamp_tags:
            return value, decoded
    return None, None

def extract_mov_creation_time(filepath):
    # Optional: Use hachoir or ffprobe to get MOV metadata
    # Placeholder for now
    return None, 'N/A'

def log_error(file_path, error_message):
    write_header = not os.path.exists(error_log_file)
    with open(error_log_file, mode='a', newline='', encoding='utf-8') as error_file:
        writer = csv.writer(error_file)
        if write_header:
            writer.writerow(['File Path', 'Error Message'])
        writer.writerow([file_path, error_message])

def log_capture_time(file_path, timestamp, status, source_tag):
    write_header = not os.path.exists(timestamp_log_file)
    with open(timestamp_log_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(['File Path', 'Timestamp', 'Status', 'Source Tag'])
        writer.writerow([
            file_path,
            timestamp if timestamp else 'N/A',
            status,
            source_tag if source_tag else 'N/A'
        ])

def compress_resize_and_save(img, output_path, target_size_kb, exif=None):
    quality = 85
    while True:
        save_kwargs = {'quality': quality}
        if exif is not None:
            save_kwargs['exif'] = exif
        img.save(output_path, 'JPEG', **save_kwargs)

        file_size_kb = os.path.getsize(output_path) / 1024
        if file_size_kb <= target_size_kb:
            print(f'Processed: {output_path}, Size: {file_size_kb:.2f} KB')
            break

        quality -= 5
        if quality < 20:
            width, height = img.size
            img = img.resize((width // 2, height // 2), Image.LANCZOS)
            quality = 85

def convert_heic_to_pil(heic_path):
    heif_file = pillow_heif.read_heif(heic_path)
    return Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )

def extract_first_frame_from_mov(mov_path):
    clip = VideoFileClip(mov_path)
    frame = clip.get_frame(0)
    clip.reader.close()
    if clip.audio:
        clip.audio.reader.close_proc()
    return Image.fromarray(frame)

def process_files(input_folder, output_folder):
    global count
    for root, _, files in os.walk(input_folder):
        for file in files:
            count += 1
            if count % 100 == 0:
                print(f'{count} files processed at: {datetime.now()}')

            file_path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            ext = ext.lower()

            relative_path = os.path.relpath(root, input_folder)
            output_subfolder = os.path.join(output_folder, relative_path)
            os.makedirs(output_subfolder, exist_ok=True)

            output_file_name = f"{name}.jpg"
            output_path = os.path.join(output_subfolder, output_file_name)

            if os.path.exists(output_path):
                print(f'Skipping already processed file: {output_path}')
                try:
                    img = Image.open(file_path)
                    timestamp, source_tag = get_capture_datetime(img)
                except (UnidentifiedImageError, IOError):
                    timestamp, source_tag = None, None
                log_capture_time(file_path, timestamp, 'Skipped', source_tag)
                continue

            try:
                if ext in ['.jpg', '.jpeg']:
                    img = Image.open(file_path)
                    exif_data = img.info.get('exif')
                    compress_resize_and_save(img.convert('RGB'), output_path, target_size_kb, exif=exif_data)

                elif ext == '.png':
                    img = Image.open(file_path)
                    compress_resize_and_save(img.convert('RGB'), output_path, target_size_kb)

                elif ext == '.heic':
                    img = convert_heic_to_pil(file_path)
                    compress_resize_and_save(img.convert('RGB'), output_path, target_size_kb)

                elif ext == '.mov':
                    img = extract_first_frame_from_mov(file_path)
                    compress_resize_and_save(img.convert('RGB'), output_path, target_size_kb)

                else:
                    print(f"Unsupported file type: {file_path}, skipping.")
                    log_capture_time(file_path, None, 'Skipped', 'Unsupported Format')
                    continue

                # Timestamp logging after successful processing
                if ext == '.mov':
                    timestamp, source_tag = extract_mov_creation_time(file_path)
                else:
                    timestamp, source_tag = get_capture_datetime(img)
                log_capture_time(file_path, timestamp, 'Processed', source_tag)

            except Exception as e:
                error_message = f'Error processing {file_path}: {str(e)}\nTraceback: {traceback.format_exc()}'
                print(error_message)
                log_error(file_path, error_message)
                try:
                    img = Image.open(file_path)
                    timestamp, source_tag = get_capture_datetime(img)
                except Exception:
                    timestamp, source_tag = None, None
                log_capture_time(file_path, timestamp, 'Error', source_tag)

process_files(input_dir, output_dir)
print('All done!')
