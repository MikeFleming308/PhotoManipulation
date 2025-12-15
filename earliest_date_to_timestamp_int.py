import pandas as pd
photo_date_path = r'C:\C_working\TS19_working\INPUT\Photo_date_UTF8_with_emails.csv'

output_path = r'C:\C_working\TS19_working\INPUT\Photo_date_FINAL.csv'  # Or overwrite your input file

# Read CSV
photo_df = pd.read_csv(photo_date_path)

# Remove braces and convert bracket_date to datetime
photo_df['bracket_date'] = pd.to_datetime(photo_df['bracket_date'].str.strip('{}'), errors='coerce')

# Create Unix timestamp integer column (seconds since epoch)
# If you want milliseconds, multiply by 1000
photo_df['timestamp_int'] = photo_df['bracket_date'].astype('int64') // 10**9  # pandas datetime64[ns] to seconds as int

# Save updated dataframe
photo_df.to_csv(output_path, index=False)
print(f"Updated photo_date table with timestamp_int saved to:\n{output_path}")

