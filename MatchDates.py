import pandas as pd

# Load both datasets
survey_dates = r"C:\C_working\TS19_working\Working\TS19_Survey_dates.csv"
tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A.csv"
matched_output = r"C:\C_working\TS19_working\Working\matched_output.csv"
survey_df = pd.read_csv(survey_dates, parse_dates=["START", "END", "MID"])
updated_df = pd.read_csv(tbl_a, parse_dates=["earliest_date"])

# Prepare a list to collect matched rows
matched_rows = []

# Iterate through each row in Updated_Table_A
for _, updated_row in updated_df.iterrows():
    earliest_date = updated_row["earliest_date"]

    # Filter survey_df where MID is between START and END
    matches = survey_df[(survey_df["START"] <= earliest_date) & (survey_df["END"] >= earliest_date)]

    # matches = survey_df[
    #     (survey_df["MID"] >= survey_df["START"]) &
    #     (survey_df["MID"] <= survey_df["END"]) &
    #     (survey_df["MID"] == earliest_date)
    # ]

    # If matches found, combine with updated_row
    for _, match_row in matches.iterrows():
        combined_row = updated_row.to_dict()
        for col in ["objectid", "globalid", "site", "inspector", "duration_hours", "FLAG", "START", "END", "MID"]:
            combined_row[col] = match_row[col]
        matched_rows.append(combined_row)

# Convert to DataFrame
output_df = pd.DataFrame(matched_rows)

# Save to CSV
output_df.to_csv(matched_output, index=False)

print("Matching complete. Output saved to matched_output.csv.")
