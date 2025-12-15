import pandas as pd

# File paths
in_csv = r'path_to_input.csv'
out_csv = r'path_to_output.csv'

# Read CSV
df = pd.read_csv(in_csv)

# Remove curly braces and parse datetime columns
df['START'] = pd.to_datetime(df['txt_insp_date'].str.strip('{}'), format='%Y-%m-%d %H:%M:%S', errors='coerce')
df['END'] = pd.to_datetime(df['txt_insp_date_end'].str.strip('{}'), format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Calculate midpoint datetime
df['MID_dt'] = df['START'] + (df['END'] - df['START']) / 2

# Format MID as string
df['MID'] = df['MID_dt'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Calculate duration in seconds (float)
df['seconds_duration'] = (df['END'] - df['START']).dt.total_seconds()

# Drop intermediate datetime columns if not needed
df.drop(columns=['START', 'END', 'MID_dt'], inplace=True)

# Save to output CSV
df.to_csv(out_csv, index=False)
