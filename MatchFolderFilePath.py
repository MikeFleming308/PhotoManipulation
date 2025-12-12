import pandas as pd
import os

tbl_a = r"C:\C_working\TS19_working\Working\Table_A.csv"
tbl_b = r"C:\C_working\TS19_working\Working\Table_B.csv"
updated_tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A.csv"
# Load the CSV files
table_a = pd.read_csv(tbl_a)
table_b = pd.read_csv(tbl_b)

# Function to extract the last two components of the file path
def extract_key(path):
    parts = os.path.normpath(path).split(os.sep)
    return os.path.join(parts[-2], parts[-1]) if len(parts) >= 2 else parts[-1]

# Create matching keys for both tables
table_a["match_key"] = table_a["file_path"].apply(extract_key)
table_b["match_key"] = table_b["file_path"].apply(extract_key)

# Merge the tables on the match_key
merged = pd.merge(table_a, table_b, on="match_key", suffixes=('_a', '_b'), how='left')

# Fill missing values in Table A with values from Table B
columns_to_fill = ["exif_accessible", "date_times", "earliest_date", "device_id", "make", "model", "serial_number"]
for col in columns_to_fill:
    merged[col + "_a"] = merged[col + "_a"].combine_first(merged[col + "_b"])

# Prepare the updated Table A
updated_table_a = merged[[col + "_a" for col in table_a.columns if col != "match_key"]]
updated_table_a.columns = [col.replace("_a", "") for col in updated_table_a.columns]

# Save the updated Table A
updated_table_a.to_csv(updated_tbl_a, index=False)
