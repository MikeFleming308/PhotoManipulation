
import pandas as pd

# Your dictionary of team member emails
email_dict = {
    'Elton': 'elton.simpson@aurecongroup.com',
    'Ayman': 'daina.harrison@aurecongroup.com',
    'Patrick': 'patrick.musial@aurecongroup.com',
    'Jefferson': 'jefferson.lee@aurecongroup.com',
    'Daina': 'daina.harrison@aurecongroup.com',
    'Colin': 'colin.sheldon@aurecongroup.com',
    'Greg': 'greg.andersen@aurecongroup.com',
    'Nicole': 'nicole.navarrete@aurecongroup.com',
    'Erin': 'erin.trinca@aurecongroup.com',
    'John': 'john.francis@aurecongroup.com',
    'Nishi': 'colin.sheldon@aurecongroup.com',
    'Ben': 'ben.wylie@aurecongroup.com'
}

in_csv = r"C:\C_working\TS19_working\INPUT\Photo_date_UTF8.csv"
out_csv = r'C:\C_working\TS19_working\INPUT\Photo_date_UTF8_with_emails.csv'

df = pd.read_csv(in_csv)

def get_up_to_two_emails(path):
    if not isinstance(path, str) or pd.isna(path):
        return pd.Series(['', ''])
    path_lower = path.lower()
    found_emails = []
    checked_names = set()
    for name, email in email_dict.items():
        name_lower = name.lower()
        if name_lower in path_lower and email.lower() not in found_emails and name_lower not in checked_names:
            found_emails.append(email.lower())
            checked_names.add(name_lower)
        if len(found_emails) == 2:
            break
    email_1 = found_emails[0] if len(found_emails) > 0 else ''
    email_2 = found_emails[1] if len(found_emails) > 1 else ''
    return pd.Series([email_1, email_2])




# def get_up_to_two_emails(path):
#     if not isinstance(path, str) or pd.isna(path):
#         # Return empty emails if path is not a valid string
#         return pd.Series(['', ''])
#
#     path_lower = path.lower()
#     found_emails = []
#     checked_names = set()
#     for name, email in email_dict.items():
#         name_lower = name.lower()
#         if name_lower in path_lower and email not in found_emails and name_lower not in checked_names:
#             found_emails.append(email.lower())
#             checked_names.add(name_lower)
#         if len(found_emails) == 2:
#             break
#     email_1 = found_emails[0] if len(found_emails) > 0 else ''
#     email_2 = found_emails[1] if len(found_emails) > 1 else ''
#     return pd.Series([email_1, email_2])


# def get_up_to_two_emails(path):
#     path_lower = path.lower()
#     found_emails = []
#     checked_names = set()
#     for name, email in email_dict.items():
#         name_lower = name.lower()
#         if name_lower in path_lower and email not in found_emails and name_lower not in checked_names:
#             found_emails.append(email.lower())
#             checked_names.add(name_lower)
#         if len(found_emails) == 2:
#             break
#     # Return two emails as separate values or empty string if not found
#     email_1 = found_emails[0] if len(found_emails) > 0 else ''
#     email_2 = found_emails[1] if len(found_emails) > 1 else ''
#     return pd.Series([email_1, email_2])

# Create columns if they don't exist
if 'email_1' not in df.columns:
    df['email_1'] = ''
if 'email_2' not in df.columns:
    df['email_2'] = ''

def apply_emails(row):
    if pd.notna(row['email_1']) and row['email_1'].strip() != '':
        # Return existing emails as Series to match expected output structure
        return pd.Series([row['email_1'], row['email_2'] if pd.notna(row['email_2']) else ''])
    else:
        return get_up_to_two_emails(row['file_path'])


# def apply_emails(row):
#     # Skip if email_1 already has a value
#     if pd.notna(row['email_1']) and row['email_1'].strip() != '':
#         return row[['email_1','email_2']]
#     else:
#         return get_up_to_two_emails(row['file_path'])

# Apply only on rows where email_1 is empty or NaN
new_emails = df.apply(apply_emails, axis=1)
new_emails.columns = ['email_1', 'email_2']
df[['email_1', 'email_2']] = new_emails

# Save to CSV
df.to_csv(out_csv, index=False)

