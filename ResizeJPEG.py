from PIL import Image
import os
input_dir = r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos\Trip 2 - Benalla\Photos\Benalla Day 02 - Colin'
output_dir = r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - 02 GIS\522272_GWEO_TS19_Survey\Working\MF\Trip2_d2_Benalla_Colin'

pic_size_kb = 500


def compress_and_resize_image(input_folder, output_folder, target_size_kb):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        print(filename)
                
        if filename.lower().endswith(('.jpg', '.jpeg')):
            file_path = os.path.join(input_folder, filename)
            img = Image.open(file_path)
            
            # Extract Exif data
            exif_data = img.info.get('exif')
            
            quality = 85

            while True:
                output_path = os.path.join(output_folder, filename)
                img.save(output_path, 'JPEG', quality=quality, exif=exif_data)
                file_size_kb = os.path.getsize(output_path) / 1024

                if file_size_kb <= target_size_kb:
                    break

                quality -= 5
                if quality < 20:
                    width, height = img.size
                    img = img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)
                    quality = 85

# Example usage
compress_and_resize_image(input_dir, output_dir, pic_size_kb)

print('\t', 'All done!')