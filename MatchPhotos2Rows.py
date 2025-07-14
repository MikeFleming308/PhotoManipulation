import os
import pandas as pd
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS



# Variables
photos_folder = 'path_to_your_photos'
photos = os.listdir(photos_folder)
survey_data = pd.read_csv('path_to_your_survey_data.csv')
matched_photos = []

# Functions
def extract_date_from_exif(image_path):
    image = Image.open(image_path)
    exif = image._getexif()
    for tag, value in exif.items():
        if TAGS.get(tag) == 'DateTime':
            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    return None

survey_data['Date'] = pd.to_datetime(survey_data['Date'])  # Convert to datetime

for photo in photos:
    photo_path = os.path.join(photos_folder, photo)
    # Try extracting date from filename first
    photo_date = extract_date_from_filename(photo_path)
    # If that doesn't work, try EXIF
    # photo_date = extract_date_from_exif(photo_path)

    if photo_date:
        # Find survey rows where the time is close to photo_date
        matches = survey_data[(survey_data['Date'] - pd.Timedelta(minutes=5) <= photo_date) &
                               (photo_date <= survey_data['Date'] + pd.Timedelta(minutes=5))]
        if not matches.empty:
            matched_photos.append({'photo': photo, 'matches': matches})

# Optionally, transform matched_photos into a DataFrame or another format for easier handling

matched_df = pd.DataFrame(matched_photos)
matched_df.to_csv('matched_photos.csv', index=False)









