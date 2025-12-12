import pandas as pd
import os
from pathlib import Path
from PIL import Image, ImageFile
import pillow_heif
from moviepy.editor import VideoFileClip
import io
import shutil
import logging

# To handle truncated images gracefully
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Setup logging
logging.basicConfig(
    filename='image_processing.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
INPUT_CSV = r"C:\C_working\TS19_working\Working\MasterTEST.csv"
OUTPUT_BASE_FOLDER = r"C:\C_working\TS19_working\Working\OUTPUT"

MAX_FILESIZE_BYTES = 500 * 1024  # 500 KB

# Supported extensions for images and videos
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.heic'}
VIDEO_EXTS = {'.mov'}

def load_image(file_path: Path):
    ext = file_path.suffix.lower()
    try:
        if ext in IMAGE_EXTS:
            if ext == '.heic':
                heif_file = pillow_heif.read_heif(str(file_path))
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw"
                )
            else:
                image = Image.open(file_path)
            image.load()  # force loading now to catch errors early
            return image
        elif ext in VIDEO_EXTS:
            clip = VideoFileClip(str(file_path))
            frame = clip.get_frame(0)  # get first frame
            image = Image.fromarray(frame)
            clip.reader.close()
            clip.audio.reader.close_proc()
            return image
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as e:
        raise RuntimeError(f"Failed to load image/video '{file_path}': {e}")

def save_jpeg_under_size(image: Image.Image, output_path: Path, max_bytes: int):
    """Save JPEG adjusting quality to fit under max_bytes, keep aspect ratio of image."""
    # Convert mode to RGB if not already (for JPEG)
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')

    # Try decreasing quality to get under max_bytes
    for quality in range(95, 10, -5):
        temp_buffer = io.BytesIO()
        image.save(temp_buffer, format='JPEG', quality=quality)
        size = temp_buffer.tell()
        if size <= max_bytes:
            with open(output_path, 'wb') as f_out:
                f_out.write(temp_buffer.getvalue())
            return True, quality, size
    # If can't get below max_bytes even at quality=15
    # Save anyway at low quality and return False
    image.save(output_path, format='JPEG', quality=15)
    real_size = output_path.stat().st_size
    return False, 15, real_size

def resize_image_to_fit(image: Image.Image, max_bytes: int):
    """Reduce image size by resizing (keeping aspect ratio) and compressing to fit max_bytes."""
    # Start with original image and try saving at max quality
    orig_img = image
    orig_w, orig_h = image.size
    min_scale = 0.1  # minimum scale factor to avoid too small
    scale = 1.0
    step = 0.9  # scale down by 10% each try
    best_image = image
    last_success = False

    while scale >= min_scale:
        if scale < 1.0:
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            img_resized = orig_img.resize((new_w, new_h), Image.LANCZOS)
        else:
            img_resized = orig_img

        # Check if fits under max_bytes with decent quality
        temp_buffer = io.BytesIO()
        try:
            img_resized.save(temp_buffer, format='JPEG', quality=85)
        except Exception:
            break  # Can't save, break loop
        size = temp_buffer.tell()
        if size <= max_bytes:
            best_image = img_resized
            last_success = True
            break
        # else try smaller
        scale *= step

    if not last_success:
        # Fallback: accept best found (smallest scale)
        best_image = img_resized

    return best_image

def process_row(row: pd.Series):
    info = {
        'success': False,
        'resized': False,
        'error_message': '',
        'output_folder': '',
        'jpeg_quality': None,
        'final_size_bytes': None,
        'copied_full_size_due_to_error': False,
    }
    info['output_image_path'] = str(output_path.resolve())
    try:
        original_path = Path(row['file_path'])
        if not original_path.is_file():
            msg = f"File not found: {original_path}"
            logging.error(msg)
            info['error_message'] = msg
            return info

        group_name = str(row.get('objectid') or 'ungrouped').strip()
        print(f"Grouping folder name (objectid): '{group_name}'")
        unique_name = str(row.get('photo_name') or original_path.stem).strip()

        # Prepare output folder and path
        output_folder = Path(OUTPUT_BASE_FOLDER) / group_name
        output_folder.mkdir(parents=True, exist_ok=True)
        print(f"Created/using output folder: {output_folder}")

        info['output_folder'] = str(output_folder.resolve())

        output_file_name = unique_name + '.jpg'  # force lower case extension
        output_path = output_folder / output_file_name

        # Load image/video frame
        image = load_image(original_path)

        # Attempt resize and compression
        try:
            resized_image = resize_image_to_fit(image, MAX_FILESIZE_BYTES)
            # Save with compression under size
            saved_ok, quality_used, saved_size = save_jpeg_under_size(resized_image, output_path, MAX_FILESIZE_BYTES)

            info['success'] = True
            info['resized'] = (resized_image.size != image.size)
            info['jpeg_quality'] = quality_used
            info['final_size_bytes'] = saved_size
        except Exception as e:
            # On e.g. "image file truncated" or other resize issues, copy full size and rename file
            err_msg = str(e)
            logging.warning(f"Resize/Save failed for {original_path}: {err_msg}. Copying original instead.")
            info['error_message'] = f"Resize/Save error: {err_msg}. Copied full size."
            info['copied_full_size_due_to_error'] = True
            # Copy original file to output folder with renamed filename (force .jpg extension)
            # If original is not jpg, convert full size image to jpg, else just copy
            ext = original_path.suffix.lower()
            if ext != '.jpg':
                # Convert original full size image to jpg as fallback
                fallback_img = image.convert('RGB')
                fallback_img.save(output_path, 'JPEG', quality=95)
                info['final_size_bytes'] = output_path.stat().st_size
                info['success'] = True
                info['resized'] = False
            else:
                shutil.copy2(original_path, output_path)
                info['final_size_bytes'] = output_path.stat().st_size
                info['success'] = True
                info['resized'] = False

    except Exception as e:
        msg = f"Fatal error processing file '{row.get('file_path')}': {e}"
        logging.error(msg)
        info['error_message'] = msg

    return info

def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"CSV loaded with {len(df)} rows.")
    print(df.head())

    # Prepare columns for logging results
    df['processing_success'] = False
    df['resized_image'] = False
    df['processing_error'] = ''
    df['output_folder_path'] = ''
    df['output_image_path'] = ''
    df['jpeg_quality_used'] = None
    df['final_file_size_bytes'] = None
    df['copied_full_size_due_to_error'] = False

    for idx, row in df.iterrows():
        file_path = row.get('file_path')
        print(f"Processing row {idx + 1}/{len(df)}: {file_path}")
        logging.info(f"Processing row {idx + 1}/{len(df)}: {file_path}")

        try:
            result = process_row(row)
        except Exception as e:
            result = {
                'success': False,
                'resized': False,
                'error_message': str(e),
                'output_folder': '',
                'jpeg_quality': None,
                'final_size_bytes': None,
                'copied_full_size_due_to_error': True,
                'output_image_path': ''
            }

        print(f"Output folder: {result.get('output_folder', '')}")
        print(f"Success: {result.get('success', False)} Resized: {result.get('resized', False)}")

        df.at[idx, 'processing_success'] = result.get('success', False)
        df.at[idx, 'resized_image'] = result.get('resized', False)
        df.at[idx, 'processing_error'] = result.get('error_message', '')
        df.at[idx, 'output_folder_path'] = result.get('output_folder', '')
        df.at[idx, 'output_image_path'] = result.get('output_image_path', '')
        df.at[idx, 'jpeg_quality_used'] = result.get('jpeg_quality', None)
        df.at[idx, 'final_file_size_bytes'] = result.get('final_size_bytes', None)
        df.at[idx, 'copied_full_size_due_to_error'] = result.get('copied_full_size_due_to_error', False)

    # Save the updated DataFrame to a CSV
    output_csv = Path(OUTPUT_BASE_FOLDER) / "image_processing_results.csv"
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()
