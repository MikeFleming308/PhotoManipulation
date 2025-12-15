

"""
Notes: This script takes 2 input tables;
1. A .csv file with an integer field holding datetime values as UNIX timestamps that have been extracted from the EXIF
2. A copy of the Survey123 feature service as a .csv with START and END datetime values as UNIX timestamps

The script compares the photo date and time with the period between START and END datetime to make a match. But only if
the email address of the person logged into Survey123 matches an email derived from the folder path of the image file.

If a match is made, all fields from both input tables are included on a new row in the output table "Master.csv"

Once "Master.csv" is created, it is used by another script (Export_imagesV2.py) to copy, rename, resize and
standardise the image format to .jpg

The photo_df's multi-email email field is split into rows with single emails, ensuring photo_df['email']
is 1-dimensional and suitable for grouping and matching.
All emails and user fields are lowercased and whitespace-trimmed for consistent matching.
Date parsing is robust to malformed strings by stripping braces {} and using errors='coerce'.
Final output prefixes columns to distinguish source tables and is saved if matches exist.
"""

import pandas as pd

# Paths to your files
photo_date_path = r'C:\C_working\TS19_working\INPUT\Photo_date_UTF8_with_emails.csv'
s123_path = r'C:\C_working\TS19_working\INPUT\S123_UTF8_No_Excel.csv'
master_output_path = r"C:\C_working\TS19_working\OUTPUT\Master.csv"

# --- Read photo_date CSV ---
photo_df = pd.read_csv(photo_date_path)

# Remove braces and parse earliest_date as datetime
photo_df['earliest_date'] = pd.to_datetime(photo_df['earliest_date'].str.strip('{}'), errors='coerce')
#
# # Normalize and split 'email' column into lists, then explode into separate rows
# photo_df['email'] = photo_df['email'].astype(str).str.lower().str.strip()
# photo_df['email_list'] = photo_df['email'].str.split(',')
#
# photo_df = photo_df.explode('email_list').reset_index(drop=True)
# photo_df['email_list'] = photo_df['email_list'].str.strip()
#
# # Drop empty or NaN emails
# photo_df = photo_df[photo_df['email_list'].notna() & (photo_df['email_list'] != '')]
#
# # Rename exploded email column for clarity
# photo_df = photo_df.rename(columns={'email_list': 'email'})

# --- Read s123 CSV ---
s123_df = pd.read_csv(s123_path)

# Remove braces and parse inspection dates as datetime
s123_df['txt_insp_date'] = pd.to_datetime(s123_df['txt_insp_date'].str.strip('{}'), errors='coerce')
s123_df['txt_insp_date_end'] = pd.to_datetime(s123_df['txt_insp_date_end'].str.strip('{}'), errors='coerce')

# Normalize 'created_user' emails (single email per row)
s123_df['created_user'] = s123_df['created_user'].astype(str).str.lower().str.strip()

# --- Prepare matching ---

# Group photo_df by email for efficient lookup
photo_grouped = photo_df.groupby('email')

matched_rows = []

for idx, srow in s123_df.iterrows():
    user_email = srow['created_user']

    # Skip if user_email is missing or no photos for this email
    if not user_email or user_email not in photo_grouped.groups:
        continue

    candidate_photos = photo_grouped.get_group(user_email)

    insp_start = srow['txt_insp_date']
    insp_end = srow['txt_insp_date_end']

    # Skip if inspection dates are invalid
    if pd.isna(insp_start) or pd.isna(insp_end):
        continue

    # Match photo earliest_date between inspection start and end
    mask = (candidate_photos['earliest_date'] >= insp_start) & (candidate_photos['earliest_date'] <= insp_end)
    matched_photos = candidate_photos.loc[mask]

    # If none matched and inspection > 10 mins, try 10-min window after start
    if matched_photos.empty:
        inspection_duration = (insp_end - insp_start).total_seconds() / 60
        max_end = insp_start + pd.Timedelta(minutes=10) if inspection_duration > 10 else insp_end

        mask = (candidate_photos['earliest_date'] >= insp_start) & (candidate_photos['earliest_date'] <= max_end)
        matched_photos = candidate_photos.loc[mask]

    if matched_photos.empty:
        continue  # No matches for this s123 record

    # If more than 10 matches, keep 10 closest earliest_date to insp_start
    if len(matched_photos) > 10:
        matched_photos = matched_photos.copy()
        matched_photos['time_diff'] = (matched_photos['earliest_date'] - insp_start).abs()
        matched_photos = matched_photos.nsmallest(10, 'time_diff').drop(columns=['time_diff'])

    # Combine matched photo rows with current s123 row adding prefixes
    for _, photo_row in matched_photos.iterrows():
        s123_prefixed = srow.add_prefix('s123_')
        photo_prefixed = photo_row.add_prefix('photo_')
        combined = pd.concat([s123_prefixed, photo_prefixed])
        matched_rows.append(combined)

# --- Output results ---
if matched_rows:
    master_df = pd.DataFrame(matched_rows).reset_index(drop=True)
    master_df.to_csv(master_output_path, index=False)
    print(f"Saved combined Master.csv: {master_output_path}")
else:
    print("No matching records found based on criteria.")
