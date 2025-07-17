import pandas as pd
from datetime import datetime, timedelta

# in_csv = r'C:\C_working\TS19_working\S123_CSV\TEST_CSV.csv'
# out_csv = r'C:\C_working\TS19_working\S123_CSV\OUT_CSV.csv'
in_csv = r'C:\C_working\TS19_working\S123_CSV\TS19_Survey_datesCorrected.csv'
out_csv = r'C:\C_working\TS19_working\S123_CSV\TS19_Survey_dates.csv'

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
