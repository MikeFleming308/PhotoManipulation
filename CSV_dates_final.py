import pandas as pd
from datetime import datetime, timedelta

# Load the CSV file
in_csv = "S123_tbl.csv"
out_csv = "TS19_Survey_dates_processed.csv"
df = pd.read_csv(in_csv)

# Define the columns for start and end times
start_col = "inspect_date"
end_col = "inspect_end"

# Function to parse datetime with multiple formats
def parse_datetime(dt_str):
    if pd.isna(dt_str):
        return None
    for fmt in ("%d/%m/%Y, %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None

# Apply parsing and convert to AEST (UTC + 10 hours)
df["START_dt"] = df[start_col].apply(parse_datetime).apply(lambda x: x + timedelta(hours=10) if x else None)
df["END_dt"] = df[end_col].apply(parse_datetime).apply(lambda x: x + timedelta(hours=10) if x else None)

# Calculate durations
df["duration_hours"] = ((df["END_dt"] - df["START_dt"]).dt.total_seconds() / 3600).round(2)
df["seconds_duration"] = ((df["END_dt"] - df["START_dt"]).dt.total_seconds()).astype("Int64")

# Flag long durations
df["long_duration_flag"] = df["duration_hours"] > 2

# Format timestamps
df["START"] = df["START_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["END"] = df["END_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["MID"] = ((df["START_dt"] + (df["END_dt"] - df["START_dt"]) / 2).dt.strftime("%Y-%m-%d %H:%M:%S"))

# Drop intermediate datetime columns
df.drop(columns=["START_dt", "END_dt"], inplace=True)

# Save the cleaned output
df.to_csv(out_csv, index=False)
