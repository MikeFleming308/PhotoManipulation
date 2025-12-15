import pandas as pd

"""
Matching s123.created_user against either photo_email_1 or email_2
Matching s123.START_unix and s123.END_unix integer timestamps with photo.timestamp_int (in seconds since epoch), using the
time window rules as before.

Notes:
The script assumes your updated tables have these exact column names:
photo table: timestamp_int (int UNIX timestamp), email_1, email_2 (strings)
s123 table: created_user (string), START_unix (int UNIX timestamp), END_unix (int UNIX timestamp)
Matching an s123.created_user against either email_1 or email_2.
Time matching is purely integer comparison of UNIX timestamps (seconds since epoch).
Keeps up to 10 closest photos by timestamp difference when there are more than 10 matches.
Outputs combined columns prefixed s123_ and photo_ as before.
"""

# Create_Master_int_dates
"""
Matching s123.created_user against email_1 or email_2 fields in photo_df.
Matching integer UNIX timestamps between s123.START_unix and END_unix fields against photo.timestamp_int.
"""

# File paths
# with email_1/2 and timestamp_int

photo_date_path = r'C:\C_working\TS19_working\INPUT\Photo_date_FINAL.csv'
s123_path = r'C:\C_working\TS19_working\INPUT\S123_UTF8_No_Excel.csv'

# photo_date_path = r'C:\C_working\TS19_working\INPUT\Earliest_date_sample_updated.csv'
# s123_path = r'C:\C_working\TS19_working\INPUT\S123_sample_updated.csv'  # with START_unix and END_unix integer timestamps
master_output_path = r'C:\C_working\TS19_working\OUTPUT\Master.csv'

# Load data
photo_df = pd.read_csv(photo_date_path)
s123_df = pd.read_csv(s123_path)

# Normalize email columns: lowercase and strip spaces, replace 'nan' strings with empty
for col in ['email_1', 'email_2']:
    photo_df[col] = photo_df[col].replace('nan', '').astype(str).str.lower().str.strip()

s123_df['created_user'] = s123_df['created_user'].astype(str).str.lower().str.strip()

# Debug prints about loaded email data
print("\nPhoto dataframe email info:")
print(f"Photo table loaded: {len(photo_df)} rows")

unique_photo_emails_1 = photo_df['email_1'].unique()
unique_photo_emails_2 = photo_df['email_2'].unique()

print(f"Unique photo_emails_1 count: {len(unique_photo_emails_1)}")
print(f"Sample photo_emails_1: {unique_photo_emails_1[:5]}")
print(f"Unique photo_emails_2 count: {len(unique_photo_emails_2)}")
print(f"Sample photo_emails_2: {unique_photo_emails_2[:5]}")

print("\ns123 dataframe email info:")
print(f"s123 table loaded: {len(s123_df)} rows")
unique_s123_emails = s123_df['created_user'].unique()
print(f"Unique s123 created_user emails count: {len(unique_s123_emails)}")
print(f"Sample s123 emails: {unique_s123_emails[:5]}")

# Check overall overlap between photo emails and s123 emails separately for _1 and _2
common_emails_1 = set(unique_photo_emails_1) & set(unique_s123_emails) - {''}
common_emails_2 = set(unique_photo_emails_2) & set(unique_s123_emails) - {''}

print(f"\nNumber of emails common to email_1 and created_user: {len(common_emails_1)}")
print(f"Number of emails common to email_2 and created_user: {len(common_emails_2)}")

if len(common_emails_1) == 0:
    print("Warning: No overlapping emails found between email_1 and created_user.")
if len(common_emails_2) == 0:
    print("Warning: No overlapping emails found between email_2 and created_user.")

matched_rows = []

# Loop through s123 rows and try to match photos by email and timestamp
for idx, srow in s123_df.iterrows():
    user_email = srow['created_user']
    insp_start = srow['START_unix']
    insp_end = srow['END_unix']

    # Skip rows with invalid or missing data
    if not user_email or pd.isna(insp_start) or pd.isna(insp_end):
        continue

    # Filter photos where created_user matches either email_1 or email_2
    photo_candidates = photo_df[
        (photo_df['email_1'] == user_email) | (photo_df['email_2'] == user_email)
    ]

    if photo_candidates.empty:
        print(f"No photo emails matching s123 created_user '{user_email}' at s123 row {idx}")
        continue

    # Debug print: how many photo candidates for this user (print every 500 rows)
    if idx % 500 == 0:
        print(f"s123 row {idx} user {user_email} - photo candidates found: {len(photo_candidates)}")

    # Match photo timestamp_int between START_unix and END_unix timestamps inclusive
    mask = (photo_candidates['timestamp_int'] >= insp_start) & (photo_candidates['timestamp_int'] <= insp_end)
    matched_photos = photo_candidates.loc[mask]

    # If no matches and inspection > 10 minutes, limit window to 10 mins after START_unix
    if matched_photos.empty:
        inspection_length_min = (insp_end - insp_start) / 60
        max_end = insp_start + 600 if inspection_length_min > 10 else insp_end

        mask = (photo_candidates['timestamp_int'] >= insp_start) & (photo_candidates['timestamp_int'] <= max_end)
        matched_photos = photo_candidates.loc[mask]

    if matched_photos.empty:
        # Find and print closest photo timestamp for diagnosis
        photo_candidates = photo_candidates.copy()
        photo_candidates['time_diff'] = (photo_candidates['timestamp_int'] - insp_start).abs()
        closest_photo = photo_candidates.nsmallest(1, 'time_diff').iloc[0]
        closest_ts = closest_photo['timestamp_int']
        time_diff_sec = abs(closest_ts - insp_start)
        print(f"No matching photo timestamps within window for '{user_email}' at s123 row {idx}.")
        print(f"Closest photo ts: {closest_ts} (diff {time_diff_sec} seconds from START_unix)")
        continue

    print(f"Matching photos found for '{user_email}' at s123 row {idx}, count: {len(matched_photos)}")

    # Limit output to at most 10 closest photos by timestamp difference to START_unix
    if len(matched_photos) > 10:
        matched_photos = matched_photos.copy()
        matched_photos['time_diff'] = (matched_photos['timestamp_int'] - insp_start).abs()
        matched_photos = matched_photos.nsmallest(10, 'time_diff').drop(columns=['time_diff'])

    for _, photo_row in matched_photos.iterrows():
        s123_prefixed = srow.add_prefix('s123_')
        photo_prefixed = photo_row.add_prefix('photo_')
        combined = pd.concat([s123_prefixed, photo_prefixed])
        matched_rows.append(combined)

if matched_rows:
    master_df = pd.DataFrame(matched_rows).reset_index(drop=True)
    master_df.to_csv(master_output_path, index=False)
    print(f"\nMaster.csv saved to: {master_output_path}")
else:
    print("\nNo matching records found based on criteria.")
