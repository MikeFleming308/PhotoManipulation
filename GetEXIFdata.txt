import os
import arcpy
import pandas as pd
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

# Define the root directory containing the photos and the name of the geodatabase table
root_dir = r'C:\C_working\TS19_working\Resized'  # Change this to your root directory
gdb_path = r'C:\C_working\TS19_working\Cwork.gdb'
table_name = 'PhotoEXIFInfo'  # The name for the new table

# Create the schema for the geodatabase table
fields = [
    ('file_path', 'TEXT'),
    ('date_time', 'DATE'),
    ('device_id', 'TEXT'),
    ('make', 'TEXT'),
    ('model', 'TEXT'),
    ('serial_number', 'TEXT'),
    ('exif_accessible', 'TEXT')
]

# Create the geodatabase table if it does not exist
table = os.path.join(gdb_path, table_name)
if not arcpy.Exists(table):
    arcpy.CreateTable_management(gdb_path, table_name)
    for field in fields:
        arcpy.AddField_management(table, field[0], field[1])

def extract_exif(image_path):
    """Extract EXIF data from image and return relevant attributes."""
    exif_data = {}
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
    except Exception as e:
        exif_data['Error'] = str(e)
    return exif_data

# Traverse through all the folders and files within the root directory
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.lower().endswith('.jpg'):
            file_path = os.path.join(dirpath, filename)
            exif_data = extract_exif(file_path)

            # Prepare data for table
            file_info = {
                'file_path': file_path,
                'date_time': None,
                'device_id': None,
                'make': None,
                'model': None,
                'serial_number': None,
                'exif_accessible': 'Yes'
            }

            # Extract fields of interest
            if 'DateTimeOriginal' in exif_data:
                file_info['date_time'] = datetime.strptime(exif_data['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
            else:
                file_info['exif_accessible'] = 'No'

            file_info['make'] = exif_data.get('Make', None)
            file_info['model'] = exif_data.get('Model', None)
            file_info['device_id'] = exif_data.get('ImageUniqueID', None)
            file_info['serial_number'] = exif_data.get('SerialNumber', None)

            # Insert the data into the geodatabase table
            with arcpy.da.InsertCursor(table, [field[0] for field in fields]) as cursor:
                cursor.insertRow((file_info['file_path'], file_info['date_time'], file_info['device_id'],
                                  file_info['make'], file_info['model'], file_info['serial_number'],
                                  file_info['exif_accessible']))

print("EXIF information extraction and saving completed.")
