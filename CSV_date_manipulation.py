# C:\C_working\Python_scripts\PhotoManipulation\CSV_date_manipulation.py

import pandas as pd
from datetime import datetime, timedelta
"""
Purpose of the script (process and analyze survey date data from CSV files): The script reads survey date and time data 
from an input CSV file, parses and converts these date-time strings into datetime objects with timezone adjustment 
(UTC to AEST), and calculates the duration between start and end times. Duration calculation and flagging (identify 
records with long durations): It computes the duration in hours between the start and end timestamps, then flags 
records  where this duration exceeds 2 hours. Date formatting and midpoint computation (generate formatted date 
strings and midpoint timestamp): The script formats the start, end, and midpoint dates in a consistent string format 
and removes intermediate datetime columns for cleaner output. 

Output generation (save processed data into a new CSV file): Finally, it saves the cleaned and enriched dataset, 
including flags and calculated fields, to an output CSV file for  further use or analysis.

Input: CSV export from S123 website or csv previously output from this script. (eg, run script, identify problem dates, adjust in 
"inspect_date" and "inspect_end" fields and run again as input.

Output: TS19_Survey_dates.csv'
"""




# in_csv = r'C:\C_working\TS19_working\S123_CSV\TEST_CSV.csv'

in_csv = r"C:\C_working\TS19_working\Working\S123_CSV\S123_tbl.csv"
out_csv = r'C:\C_working\TS19_working\Working\S123_CSV\TS19_Survey_dates_processed.csv'

# Read your CSV
df = pd.read_csv(in_csv)

# Define a flexible parser with UTC adjustment
def parse_datetime(text, formats):
    if pd.isna(text):
        return None
    for fmt in formats:
        try:
            dt = datetime.strptime(str(text).strip(), fmt)
            return dt + timedelta(hours=10)  # Convert from UTC to AEST
        except ValueError:
            continue
    return None

# Formats to try
formats = [
    '%d/%m/%Y %H:%M',
    '%d/%m/%Y %H:%M:%S',
    '%m/%d/%Y %H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
]

# Parse START and END
df["START_dt"] = df["inspect_date"].apply(lambda x: parse_datetime(x, formats))
df["END_dt"] = df["inspect_end"].apply(lambda x: parse_datetime(x, formats))

# Ensure datetime columns are properly typed
df["START_dt"] = pd.to_datetime(df["START_dt"], errors='coerce')
df["END_dt"] = pd.to_datetime(df["END_dt"], errors='coerce')

# check for unparsed dates
print("Unparsed 'inspect_date' rows:")
print(df[df["START_dt"].isna()]["inspect_date"])

print("Unparsed 'inspect_end' rows:")
print(df[df["END_dt"].isna()]["inspect_end"])

# Calculate duration
df["duration_hours"] = ((df["END_dt"] - df["START_dt"]).dt.total_seconds() / 3600).astype(float).round(2)

# Flag records with duration > 2 hours
df["FLAG"] = df["duration_hours"].apply(lambda x: "Yes" if x > 2 else "No")

# Format START and END
df["START"] = df["START_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')
df["END"] = df["END_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')

# Calculate MID
df["MID_dt"] = df["START_dt"] + (df["END_dt"] - df["START_dt"]) / 2
df["MID"] = df["MID_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')

# Clean up intermediate columns
df.drop(columns=["START_dt", "END_dt", "MID_dt"], inplace=True)

# Save to CSV
df.to_csv(out_csv, index=False)
