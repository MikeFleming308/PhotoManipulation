import os
import arcpy
import pandas as pd
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS


# Variables
input_dir = r'C:\C_working\TS19_working\Resized\Trip_2_Benalla\Photos\Benalla_Day_03_Colin'
output_path = r'C:\C_working\TS19_working\matched_photos.csv'
gdb = r'C:\C_working\TS19_working\Cwork.gdb'

photos = os.listdir(input_dir)
matched_photos = []

before = 1
after = 1

in_tbl = os.path.join(gdb, "Benalla")

# columns = [f.name.lower() for f in arcpy.ListFields(in_tbl)]
columns = ['objectid', 'globalid', 'site', 'estate_business_identifier', 'asset_id', 'location', 'inspector', 'deviceid', 'created_date']

# Functions
def extract_date_from_exif(image_path):
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if TAGS.get(tag) == 'DateTime':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
    return None

def read_to_df(dbtable,columns):
    dataList = [row for row in arcpy.da.SearchCursor(dbtable,columns)]
    if columns == '*':
        columns = [f.name.lower() for f in arcpy.ListFields(dbtable)]
    readto_df = pd.DataFrame(dataList,columns=columns)
    return readto_df


# Setup 
# Load table into a DataFrame
for col in columns:
    print(col)
in_tbl_df = read_to_df(in_tbl, columns)

# Ensure date field is in datetime format
in_tbl_df['created_date'] = pd.to_datetime(in_tbl_df['created_date'])

# in_tbl_df


# Main

for photo in photos:
    photo_path = os.path.join(input_dir, photo)
    photo_date = extract_date_from_exif(photo_path)

    if photo_date:
        matches = in_tbl_df[(in_tbl_df['created_date'] - pd.Timedelta(minutes=before) <= photo_date) & 
                         (photo_date <= in_tbl_df['created_date'] + pd.Timedelta(minutes=after))]
        if not matches.empty:
            matched_photos.append({'photo': photo, 'matches': matches})

matched_df = pd.DataFrame(matched_photos)

matched_df.to_csv(output_path, index=False)




