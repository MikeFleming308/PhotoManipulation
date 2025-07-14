from PIL import Image
import os
import traceback
import csv
from datetime import datetime

# Testing dirs
# input_dir = r'C:\C_working\TS19_working\test_input'
# output_dir = r'C:\C_working\TS19_working\test_output'

# input_dir = r'C:\C_working\TS19_working\Fullsize' 
input_dir = r'C:\C_working\TS19_working\Fullsize\Trip 4 - Mulwala'

# output_dir = r'C:\C_working\TS19_working\Resized_long_path'
output_dir = r'C:\C_working\TS19_working\Resized_long_path\Trip 4 - Mulwala'
# output_dir = r'C:\C_working\TS19_working\Resized'  

count = 0
pic_size_kb = 500

# Define the path for your CSV error log file
error_log_file = os.path.join(output_dir,'resize_error_log.csv')

# Function to log errors to a CSV file
def log_error(file_path, error_message):
    with open(error_log_file, mode='a', newline='') as error_file:
        error_writer = csv.writer(error_file)
        error_writer.writerow([file_path, error_message])


def compress_and_resize_image(input_folder, output_folder, target_size_kb, count):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            
            if filename.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(root, filename)
                count += 1
                if count % 100 == 0:
                    current_time = datetime.now()
                    print(f'\n {count} processed at: {current_time}')
                # Create a corresponding output path
                relative_path = os.path.relpath(root, input_folder)  # Get relative path from input_dir
                output_subfolder = os.path.join(output_folder, relative_path)  # Create output subfolder path
                
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)  # Ensure the output subfolder exists
                    
                output_path = os.path.join(output_subfolder, filename)
                
                # Skip existing processed files
                if os.path.exists(output_path):
                    print(f'Skipping already processed file: {output_path}')
                    continue
                
                try:
                    # Try to open the image file
                    img = Image.open(file_path)
                    
                    # Extract Exif data
                    exif_data = img.info.get('exif')
                    
                    quality = 85

                    while True:
                        img.save(output_path, 'JPEG', quality=quality, exif=exif_data)
                        file_size_kb = os.path.getsize(output_path) / 1024

                        if file_size_kb <= target_size_kb:
                            print(f'Processed: {output_path}, Size: {file_size_kb:.2f} KB')
                            break

                        quality -= 5
                        if quality < 20:
                            width, height = img.size
                            img = img.resize((width // 2, height // 2), Image.LANCZOS)
                            quality = 85

                except Exception as e:
                    print(f'Error processing file "{file_path}": {e}')
                    error_message = f'Error processing file "{file_path}": {str(e)}\nTraceback: {traceback.format_exc()}'
                    print(error_message)
                    log_error(file_path, error_message)  # Log the error




# Example usage
compress_and_resize_image(input_dir, output_dir, pic_size_kb, count)

print('\t', 'All done!')
