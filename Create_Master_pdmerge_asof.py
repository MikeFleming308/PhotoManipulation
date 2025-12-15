import pandas as pd

# File paths (adjust as needed)
earliest_date_csv = r"C:\C_working\TS19_working\Working\Earliest_date_std.csv"
survey_dates_csv = r"C:\C_working\TS19_working\Working\S123_CSV\TS19_Survey_dates_std.csv"
output_csv = r"C:\C_working\TS19_working\Working\Master_for_input.csv"

# Load data
df_earliest = pd.read_csv(earliest_date_csv)
df_survey = pd.read_csv(survey_dates_csv)

# Parse dates with dayfirst=True if European-style dates; coerce errors
df_earliest['earliest_date'] = pd.to_datetime(df_earliest['earliest_date'], dayfirst=True, errors='coerce')
df_survey['START'] = pd.to_datetime(df_survey['START'], errors='coerce')

# Drop unparseable rows
df_earliest = df_earliest.dropna(subset=['earliest_date']).reset_index(drop=True)
df_survey = df_survey.dropna(subset=['START']).reset_index(drop=True)

# Sort by datetime as required for merge_asof
df_earliest = df_earliest.sort_values('earliest_date').reset_index(drop=True)
df_survey = df_survey.sort_values('START').reset_index(drop=True)

# Create a column with START + 2 minutes for upper bound
df_survey['START_plus_2min'] = df_survey['START'] + pd.Timedelta(minutes=2)

# Use merge_asof to find for each earliest_date the closest START that is less than or equal to earliest_date
df_matches = pd.merge_asof(
    df_earliest,
    df_survey,
    left_on='earliest_date',
    right_on='START',
    direction='backward',
    suffixes=('_earliest', '_survey')
)

# Filter where earliest_date is within the 2-minute interval after START
mask = df_matches['earliest_date'] <= df_matches['START_plus_2min']
df_matches = df_matches[mask].copy()

# Calculate time difference in seconds for ranking
df_matches['time_diff_secs'] = (df_matches['earliest_date'] - df_matches['START']).dt.total_seconds()

# Optionally, keep only top N closest matches per earliest_date if multiple matches exist
# If you expect multiple matches per earliest_date, you can group and take top N closest
df_matches['earliest_index'] = df_matches.index
df_top_matches = df_matches.groupby('earliest_index').apply(lambda g: g.nsmallest(3, 'time_diff_secs')).reset_index(drop=True)

# Prepare output columns similarly as in your original script
earliest_cols = [col for col in df_earliest.columns if col != 'earliest_index']
survey_cols_to_keep = ['duration_hours', 'seconds_duration', 'long_duration_flag', 'START', 'END', 'MID', 'Asset_ID', 'Asset_ID_other']
output_cols = earliest_cols + survey_cols_to_keep

df_output = df_top_matches[output_cols].copy()

# Function to clean Asset_ID and Asset_ID_other for filename parts (copy from your script)
import re
def clean_asset_text(text):
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = re.sub(r'\s+', '_', str(text))
    text = re.sub(r'[^A-Za-z0-9_]', '', text)
    text = re.sub(r'_+', '_', text)
    return text

def create_out_filename(row):
    uid = str(row.get('UID', ''))
    asset_id = str(row.get('Asset_ID', '')).strip()
    asset_id_other = str(row.get('Asset_ID_other', '')).strip()
    if asset_id.lower() == 'other':
        processed = clean_asset_text(asset_id_other)
    else:
        processed = clean_asset_text(asset_id)
    return uid + processed

df_output['out_filename'] = df_output.apply(create_out_filename, axis=1)

# Save to CSV
df_output.to_csv(output_csv, index=False)
print(f"Output saved to {output_csv}")
