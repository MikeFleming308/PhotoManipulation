# Photo_date_to_timestamp_int.py
# Photo date to UNIX timestamp and split emails into cols.

import pandas as pd

photo_date_path = r'C:\C_working\TS19_working\INPUT\Earliest_date_sample.csv'
output_path = r'C:\C_working\TS19_working\INPUT\Earliest_date_sample_updated.csv'  # Or overwrite your input file

# Read CSV
photo_df = pd.read_csv(photo_date_path)

# Remove braces and convert earliest_date to datetime
photo_df['earliest_date'] = pd.to_datetime(photo_df['earliest_date'].str.strip('{}'), errors='coerce')

# Create Unix timestamp integer column (seconds since epoch)
# If you want milliseconds, multiply by 1000
photo_df['timestamp_int'] = photo_df['earliest_date'].astype('int64') // 10**9  # pandas datetime64[ns] to seconds as int

# Initialize new columns with empty strings
photo_df['photo_email_1'] = ''
photo_df['photo_email_2'] = ''

def process_emails(row):
    email_str = str(row['email']).strip().lower()
    emails = [e.strip() for e in email_str.split(',') if e.strip()]  # split and clean

    if len(emails) == 1:
        row['photo_email_1'] = emails[0]
        row['photo_email_2'] = ''
    elif len(emails) >= 2:
        row['photo_email_1'] = emails[0]
        row['photo_email_2'] = emails[1]
        if len(emails) > 2:
            extras = emails[2:]
            print(f"Warning: More than 2 emails in row index {row.name} - extra emails ignored: {extras}")
    else:
        # No valid emails found
        row['photo_email_1'] = ''
        row['photo_email_2'] = ''
    return row

# Apply the email processing function row-wise
photo_df = photo_df.apply(process_emails, axis=1)

# Optionally drop original 'email' column if you want:
# photo_df = photo_df.drop(columns=['email'])

# Save updated dataframe
photo_df.to_csv(output_path, index=False)
print(f"Updated photo_date table with timestamp_int and photo_email_1/2 saved to:\n{output_path}")
