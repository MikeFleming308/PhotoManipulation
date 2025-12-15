
# Start_end_mid_int_timestamp
"""
Python script that reads your s123_path CSV, converts the txt_insp_date and txt_insp_date_end datetime columns to Unix
timestamps (integers) in new columns "START" and "END", calculates the middle point "MID", and adds a
"visit_length_seconds" column representing the duration in seconds as an integer.
"""

import pandas as pd

# Paths to your files
s123_path = r'C:\C_working\TS19_working\INPUT\S123_sample.csv'
output_path = r'C:\C_working\TS19_working\INPUT\S123_sample_updated.csv'  # Modify as needed

# Read the CSV
s123_df = pd.read_csv(s123_path)

# Remove braces and parse dates
s123_df['txt_insp_date'] = pd.to_datetime(s123_df['txt_insp_date'].str.strip('{}'), errors='coerce')
s123_df['txt_insp_date_end'] = pd.to_datetime(s123_df['txt_insp_date_end'].str.strip('{}'), errors='coerce')

# Convert to Unix timestamps in seconds since epoch as integers
s123_df['START'] = s123_df['txt_insp_date'].astype('int64') // 10**9
s123_df['END'] = s123_df['txt_insp_date_end'].astype('int64') // 10**9

# Calculate MID as the midpoint unix timestamp between START and END
s123_df['MID'] = ((s123_df['START'] + s123_df['END']) // 2).astype('Int64')

# Calculate visit_length_seconds as difference between END and START
s123_df['visit_length_seconds'] = (s123_df['END'] - s123_df['START']).astype('Int64')

# Save the updated dataframe
s123_df.to_csv(output_path, index=False)
print(f"Updated s123 table saved to:\n{output_path}")