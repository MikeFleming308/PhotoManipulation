import pandas as pd
import re

# Load both datasets
survey_dates = r"C:\C_working\TS19_working\Working\Final\TS19_Survey_datesLT_30min.csv"
tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A1.csv"
matched_output = r"C:\C_working\TS19_working\Working\Final\matched_output.csv"

# Read with dayfirst=True to handle dd/mm/yyyy format correctly
survey_df = pd.read_csv(survey_dates, parse_dates=["START", "END", "MID"], dayfirst=True)
updated_df = pd.read_csv(tbl_a, parse_dates=["earliest_date"])

# survey_df = pd.read_csv(survey_dates, parse_dates=["START", "END", "MID"])
# updated_df = pd.read_csv(tbl_a, parse_dates=["earliest_date"])

# Remove rows with missing datetime in survey_df
survey_df = survey_df.dropna(subset=["START", "END"])

# Prepare a list to collect matched rows
matched_rows = []

def create_final_name(asset_id, asset_id_other):
    # Determine base string
    if asset_id == "Other":
        base_str = "Other" + str(asset_id_other or "")
    else:
        base_str = str(asset_id or "")

    # Replace specified dash patterns with underscore
    base_str = re.sub(r'(-| - |--)', '_', base_str)

    # Remove all characters except a-zA-Z0-9 and underscores
    base_str = re.sub(r'[^A-Za-z0-9_]+', '', base_str)

    # Collapse multiple underscores into a single underscore
    base_str = re.sub(r'_+', '_', base_str)

    # Remove leading/trailing underscores if any
    base_str = base_str.strip('_')

    return base_str




for _, updated_row in updated_df.iterrows():
    earliest_date = updated_row["earliest_date"]
    if pd.isna(earliest_date):
        continue

    matches = survey_df[(survey_df["START"] <= earliest_date) & (survey_df["END"] >= earliest_date)]

    for _, match_row in matches.iterrows():
        combined_row = updated_row.to_dict()
        for col in ["objectid", "globalid", "asset_id", "asset_id_other", "site", "inspector", "duration_hours", "START", "END", "MID"]:
            combined_row[col] = match_row[col]

        # Generate the Final_Name field based on asset_id and asset_id_other
        combined_row["Final_Name"] = create_final_name(combined_row.get("asset_id"), combined_row.get("asset_id_other"))

        matched_rows.append(combined_row)

output_df = pd.DataFrame(matched_rows)
output_df.to_csv(matched_output, index=False)

print("Matching complete. Output saved to matched_output.csv.")



# Iterate through each row in Updated_Table_A
# for _, updated_row in updated_df.iterrows():
#     earliest_date = updated_row["earliest_date"]
#     if pd.isna(earliest_date):
#         continue  # Skip if earliest_date is NaT
#
#     # Find matches where earliest_date is between START and END
#     matches = survey_df[(survey_df["START"] <= earliest_date) & (survey_df["END"] >= earliest_date)]
#
#     for _, match_row in matches.iterrows():
#         combined_row = updated_row.to_dict()
#         for col in ["objectid", "globalid", "asset_id", "asset_id_other", "site", "inspector", "duration_hours", "START", "END", "MID"]:
#             combined_row[col] = match_row[col]
#         matched_rows.append(combined_row)
#
# output_df = pd.DataFrame(matched_rows)
# output_df.to_csv(matched_output, index=False)
#
# print("Matching complete. Output saved to matched_output.csv.")






# for _, updated_row in updated_df.iterrows():
#     earliest_date = updated_row["earliest_date"]
#
#     # Filter survey_df where MID is between START and END
#     matches = survey_df[(survey_df["START"] <= earliest_date) & (survey_df["END"] >= earliest_date)]
#
#     # matches = survey_df[
#     #     (survey_df["MID"] >= survey_df["START"]) &
#     #     (survey_df["MID"] <= survey_df["END"]) &
#     #     (survey_df["MID"] == earliest_date)
#     # ]
#
#     # If matches found, combine with updated_row
#     for _, match_row in matches.iterrows():
#         combined_row = updated_row.to_dict()
#         for col in ["objectid", "globalid", "site", "inspector", "duration_hours", "START", "END", "MID"]:
#             combined_row[col] = match_row[col]
#         matched_rows.append(combined_row)
#
# # Convert to DataFrame
# output_df = pd.DataFrame(matched_rows)
#
# # Save to CSV
# output_df.to_csv(matched_output, index=False)
#
# print("Matching complete. Output saved to matched_output.csv.")
