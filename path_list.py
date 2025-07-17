import pandas as pd
from pathlib import Path
input_csv = r"C:\C_working\TS19_working\Working\heic.csv"
output_csv = r"C:\C_working\TS19_working\Working\heic_paths.csv"

filepath_column = 'PATH'  # adjust if your column name is different

# Read input CSV
df = pd.read_csv(input_csv)

# Extract folder path from full file path
df['folder_path'] = df[filepath_column].apply(lambda x: str(Path(x).parent))

# Get unique folder paths
unique_folders = df['folder_path'].drop_duplicates()

# Save to CSV (one folder path per line)
unique_folders.to_csv(output_csv, index=False, header=['folder_path'])

print(f"Unique folder paths written to {output_csv}")
