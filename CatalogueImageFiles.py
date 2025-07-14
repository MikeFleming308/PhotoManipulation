
import os
import csv

# Define the folder to scan
# folder_path = r"C:\C_working\TS19_working\Fullsize"
folder_path = r'C:\Users\Michael.Fleming\OneDrive - Aurecon Group\Shortcuts\522272 - GWEO - Work Order 1 - Deed Management Services - Survey Results and Photos'
output_csv = os.path.join(folder_path, "All file list.csv")

# Define known image extensions
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.mov'}

# Function to classify file type
def classify_type(extension):
    ext = extension.lower()
    if ext in image_extensions:
        return "image"
    elif ext:
        return "other"
    else:
        return "unknown"

# Collect file information
file_data = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        full_path = os.path.join(root, file)
        extension = os.path.splitext(file)[1]
        file_type = classify_type(extension)
        file_data.append([full_path, file, extension, file_type])

# Write to CSV
with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["PATH", "FILE", "EXTENSION", "TYPE"])
    writer.writerows(file_data)

print(f"CSV file created at: {output_csv}")
