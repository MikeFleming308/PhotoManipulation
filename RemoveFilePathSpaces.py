
import os
# Set your base folder path here
base_folder_path = r'C:\C_working\TS19_pics'

# Function
def rename_folders(base_folder):
    for root, dirs, files in os.walk(base_folder):
        for dir_name in dirs:
            # Create the new directory name by applying replacement rules
            new_dir_name = dir_name.replace(" - ", "_") \
                                    .replace("  ", "_") \
                                    .replace(" ", "_")
            
            # Check if renaming is needed
            if new_dir_name != dir_name:
                # Construct full old and new directory paths
                old_dir_path = os.path.join(root, dir_name)
                new_dir_path = os.path.join(root, new_dir_name)

                try:
                    # Rename the directory
                    os.rename(old_dir_path, new_dir_path)
                    print(f'Renamed: "{old_dir_path}" to "{new_dir_path}"')
                except Exception as e:
                    # Report any errors encountered during renaming
                    print(f'Error renaming "{old_dir_path}": {e}')

rename_folders(base_folder_path)

print("\t", "All done!")
