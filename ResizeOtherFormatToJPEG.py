import os
import traceback
import csv
from datetime import datetime
from PIL import Image
import pillow_heif
from moviepy.editor import VideoFileClip

print("import completed")

# User configuration: set input and output directories here
input_dir = r'C:\C_working\TS19_working\Fullsize\Trip 2 - Benalla\Photos\Benalla_Day_01_Elton'


# input_dir = r'C:\C_working\TS19_working\Fullsize\Trip 2 - Benalla'
output_dir = r'C:\C_working\TS19_working\Resized_long_path_other_format\Benalla_Day_01_Elton'

target_size_kb = 500
count = 0

# Define path for CSV error log file
error_log_file = os.path.join(output_dir, 'conversion_error_log.csv')

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Log errors to CSV file
def log_error(file_path, error_message):
    with open(error_log_file, mode='a', newline='', encoding='utf-8') as error_file:
        error_writer = csv.writer(error_file)
        error_writer.writerow([file_path, error_message])

def compress_resize_and_save(img, output_path, target_size_kb, exif=None):
    quality = 85
    while True:
        img.save(output_path, 'JPEG', quality=quality, exif=exif)
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
    frame = clip.get_frame(0)  # first frame at t=0
    clip.reader.close()
    clip.audio.reader.close_proc() if clip.audio else None
    return Image.fromarray(frame)

def process_files(input_folder, output_folder):
    global count
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            count += 1
            if count % 100 == 0:
                print(f'{count} files processed at: {datetime.now()}')

            file_path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            ext = ext.lower()

            # Calculate relative subdir and output path
            relative_path = os.path.relpath(root, input_folder)
            output_subfolder = os.path.join(output_folder, relative_path)
            if not os.path.exists(output_subfolder):
                os.makedirs(output_subfolder)

            output_file_name = f"{name}.jpg"
            output_path = os.path.join(output_subfolder, output_file_name)

            # Skip already processed files
            if os.path.exists(output_path):
                print(f'Skipping already processed file: {output_path}')
                continue

            try:
                if ext in ['.jpg', '.jpeg']:
                    # Open, compress and resize existing JPG
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

            except Exception as e:
                error_message = f'Error processing {file_path}: {str(e)}\nTraceback: {traceback.format_exc()}'
                print(error_message)
                log_error(file_path, error_message)

# Run the processing
process_files(input_dir, output_dir)
print('All done!')

