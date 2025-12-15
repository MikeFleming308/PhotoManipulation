import pandas as pd
earliest_date_csv = r"C:\C_working\TS19_working\Working\Earliest_date.csv"
survey_dates_csv = r"C:\C_working\TS19_working\Working\S123_CSV\TS19_Survey_dates_processed.csv"
earliest_date_csv_std  = r"C:\C_working\TS19_working\Working\Earliest_date_std.csv"
survey_dates_csv_std = r"C:\C_working\TS19_working\Working\S123_CSV\TS19_Survey_dates_std.csv"

def standardize_datetime(file_in, file_out, date_columns, dayfirst=True):
    df = pd.read_csv(file_in)

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=dayfirst)
        # Optional: drop rows with invalid dates or handle otherwise
        if df[col].isna().any():
            print(f"Warning: {df[col].isna().sum()} invalid dates in column '{col}' in file {file_in}")
            # For example, drop invalids:
            df = df.loc[df[col].notna()]

        # Convert to ISO format string
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Save cleaned file
    df.to_csv(file_out, index=False)
    print(f"Standardized datetime file saved as {file_out}")


# Use it on your files:
standardize_datetime(earliest_date_csv, earliest_date_csv_std, ['earliest_date'])
standardize_datetime(survey_dates_csv , survey_dates_csv_std, ['START'])

