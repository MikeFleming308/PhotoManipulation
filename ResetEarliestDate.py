import pandas as pd
from datetime import datetime
import os
import json

heic = r"C:\C_working\TS19_working\Working\HEIC"


# Load the CSV file
input_file = os.path.join(heic, "merged_csv.csv")
output_file = os.path.join(heic,"merged_reset_earliest_date.csv")
df = pd.read_csv(input_file)


# Function to extract and format the earliest datetime
def extract_earliest_datetime(date_times_str):
    if pd.isna(date_times_str):
        return None
    try:
        # Parse the JSON-like string
        date_dict = json.loads(date_times_str)
        # Convert all datetime strings to datetime objects
        datetimes = [datetime.fromisoformat(dt) for dt in date_dict.values()]
        # Find the earliest datetime
        earliest = min(datetimes)
        # Format as 'd/mm/yyyy h:mm:ss'
        return earliest.strftime("%-d/%m/%Y %H:%M:%S")
    except Exception:
        return None

# Apply the function to the 'date_times' column
df["earliest_date"] = df["date_times"].apply(extract_earliest_datetime)

# Save the updated DataFrame to a new CSV
df.to_csv(output_file, index=False)
