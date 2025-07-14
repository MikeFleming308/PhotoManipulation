import os
import arcpy
import pandas as pd
from datetime import timedelta

# Variables
gdb = r'C:\C_working\TS19_working\Cwork.gdb' 
survey_table = os.path.join(gdb, 'NIOABenalla')  # Input feature class from S123
photo_table = os.path.join(gdb, 'PhotoEXIFInfo')  # Table with extracted EXIF data
match_recs = os.path.join(gdb, 'MatchedRecords')  # Output table with matched records
s123_date_field = 'create_date_time'
# List to hold matched records
matched_records = []
# Define the time tolerance (in minutes)
time_tolerance = 1 # Set tolerance in minutes

# Load the tables into Pandas DataFrames
survey_df = pd.DataFrame(arcpy.da.TableToNumPyArray(survey_table, '*'))
photo_df = pd.DataFrame(arcpy.da.TableToNumPyArray(photo_table, '*'))

# survey_fields = arcpy.ListFields(survey_table)
# fnames = [f.name for f in survey_fields]
# print(len(survey_fields))
# for i in fnames:
#     print(i)

# Ensure date fields are in datetime format
survey_df[s123_date_field] = pd.to_datetime(survey_df[s123_date_field])  # Create pandas dataframes
photo_df['date_time'] = pd.to_datetime(photo_df['date_time'])



# Iterate through each photo entry and match it with survey records
for _, photo_row in photo_df.iterrows():
    photo_date = photo_row['date_time']
    lower_bound = photo_date - timedelta(minutes=time_tolerance)
    upper_bound = photo_date + timedelta(minutes=time_tolerance)
    
    matched_surveys = survey_df[(survey_df['create_date_time'] >= lower_bound) & (survey_df['create_date_time'] <= upper_bound)]
    
    if not matched_surveys.empty:
        count_matches = matched_surveys.shape[0]
        for _, survey_row in matched_surveys.iterrows():
            matched_records.append({
                'globalid': survey_row['globalid'],  # Replace 'globalid' with the actual unique identifier field
                'photo_path': photo_row['file_path'],
                'date_time': photo_row['date_time'],
                'count_matches': count_matches
            })

# Create a DataFrame with the matched records
output_df = pd.DataFrame(matched_records)

# Create the output table in the geodatabase
if arcpy.Exists(match_recs):
    arcpy.management.Delete(match_recs)
arcpy.CreateTable_management(gdb, 'MatchedRecords')

# Define the fields for the output table
arcpy.AddField_management(match_recs, 'globalid', 'TEXT')
arcpy.AddField_management(match_recs, 'photo_path', 'TEXT')
arcpy.AddField_management(match_recs, 'date_time', 'DATE')
arcpy.AddField_management(match_recs, 'count_matches', 'LONG')

# Insert matched records into the output table
with arcpy.da.InsertCursor(match_recs, ['globalid', 'photo_path', 'date_time', 'count_matches']) as cursor:
    for index, row in output_df.iterrows():
        cursor.insertRow((row['globalid'], row['photo_path'], row['date_time'], row['count_matches']))

print("Matching process completed and output table created.")
