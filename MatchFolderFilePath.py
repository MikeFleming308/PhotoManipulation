import pandas as pd
import os

# File paths
tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A1.csv"
tbl_b = r"C:\C_working\TS19_working\Working\HEIC\merged_csv_with_earliest_date.csv"
updated_tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A2.csv"

# Load the CSV files
table_a = pd.read_csv(tbl_a)
table_b = pd.read_csv(tbl_b)

# Function to extract the last two components of the file path
def extract_key(path):
    if not isinstance(path, str):
        return ""
    parts = os.path.normpath(path).split(os.sep)
    return os.path.join(parts[-2], parts[-1]) if len(parts) >= 2 else parts[-1]

# Create matching keys for both tables
table_a["match_key"] = table_a["file_path"].apply(extract_key) if "file_path" in table_a.columns else ""
table_b["match_key"] = table_b["file_path"].apply(extract_key)

# Merge the tables on the match_key
merged = pd.merge(table_a, table_b, on="match_key", suffixes=('_a', '_b'), how='left')

# Fill missing values in Table A with values from Table B
columns_to_fill = ["exif_accessible", "date_times", "earliest_date", "device_id", "make", "model", "serial_number"]
for col in columns_to_fill:
    col_a = col + "_a"
    col_b = col + "_b"
    if col_a in merged.columns and col_b in merged.columns:
        merged[col_a] = merged[col_a].combine_first(merged[col_b])

# Prepare the updated Table A
updated_columns = [col + "_a" for col in table_a.columns if col != "match_key" and col + "_a" in merged.columns]
updated_table_a = merged[updated_columns]
updated_table_a.columns = [col.replace("_a", "") for col in updated_table_a.columns]

# Save the updated Table A
updated_table_a.to_csv(updated_tbl_a, index=False)
