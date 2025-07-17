
import pandas as pd
from datetime import datetime, timedelta

# in_csv = r'C:\C_working\TS19_working\S123_CSV\TEST_CSV.csv'
# out_csv = r'C:\C_working\TS19_working\S123_CSV\OUT_CSV.csv'
in_csv = r'C:\C_working\TS19_working\S123_CSV\TS19_Survey.csv'
out_csv = r'C:\C_working\TS19_working\S123_CSV\TS19_Survey_dates.csv'


# Read your CSV
df = pd.read_csv(in_csv)

# Define a flexible parser function with UTC adjustment
def parse_and_adjust_datetime(text):
    if pd.isna(text):
        return None

    formats_to_try = [
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(str(text), fmt)
            dt_local = dt + timedelta(hours=10)  # Convert from UTC to AEST
            return dt_local
        except ValueError:
            continue

    print(f"Unrecognized format: {text}")
    return None

# Parse and adjust START and END
df["START_dt"] = df["inspect_date"].apply(parse_and_adjust_datetime)
df["END_dt"] = df["inspect_end"].apply(parse_and_adjust_datetime)

# Calculate time difference in hours as float
df['duration_hours'] = ((df["END_dt"] - df['START_dt']).dt.total_seconds() / 3600).astype(float)


# Round to 2 decimal places
df["duration_hours"] = df["duration_hours"].round(2)

# Flag records where duration exceeds 2 hours
df["FLAG"] = df["duration_hours"].apply(lambda x: "Yes" if x > 2 else "No")

# Format START and END
df["START"] = df["START_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')
df["END"] = df["END_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')

# Calculate MID
df["MID_dt"] = df["START_dt"] + (df["END_dt"] - df["START_dt"]) / 2
df["MID"] = df["MID_dt"].dt.strftime('%d/%m/%Y %H:%M:%S')

# Drop intermediate datetime columns
df.drop(columns=["START_dt", "END_dt", "MID_dt"], inplace=True)

# Save to CSV
df.to_csv(out_csv, index=False)


