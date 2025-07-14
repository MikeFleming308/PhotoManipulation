import arcpy
import os
from datetime import datetime

# Variables
gdb = r'C:\C_working\TS19_working\Cwork.gdb'
fc = r'NIOABenalla'
text_field = 'created_date'  # Field containing the text date
date_time_field = 'create_date_time'  # Field to store the converted datetime
fc_path = os.path.join(gdb, fc)

# Setup
arcpy.AddField_management(fc_path, date_time_field, "DATE") 

# Main
with arcpy.da.UpdateCursor(fc_path, [text_field, date_time_field]) as cursor:
    for row in cursor:
        text_date = row[0]
        if text_date:  # Check if the text_date is not None or empty
            try:
                # Convert text to datetime using the correct format
                date_time_obj = datetime.strptime(text_date, "%Y-%m-%dT%H:%M:%S")
                row[1] = date_time_obj  # Assign converted datetime to the datetime field
            except ValueError as e:
                print(f"Error processing {text_date}: {e}")
        cursor.updateRow(row)

print("Conversion completed.")
