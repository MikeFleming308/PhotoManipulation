import pandas as pd
import ast
import os
import numpy as np

tbl_a = r"C:\C_working\TS19_working\Working\Updated_Table_A2_with_emailsAnddates.csv"
df = pd.read_csv(tbl_a)

def safe_literal_eval(val):
    if pd.isna(val):
        return {}  # or return pd.NA if you want to keep missingness
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return {}  # or optionally pd.NA or the original val if preferred

df['date_times'] = df['date_times'].apply(safe_literal_eval)

def earliest_timestamp_from_dict(d):
    """
    Accepts a dict of timestamp values,
    finds the earliest timestamp,
    preserves seconds, and formats as yyyy-MM-ddTHH:mm:ss
    """
    # Defensive: if input is not dict or empty dict, return NA
    if not isinstance(d, dict) or not d:
        return pd.NA

    timestamp_strings = list(d.values())
    dates = [pd.to_datetime(ts, errors='coerce') for ts in timestamp_strings]
    dates = [dt for dt in dates if pd.notna(dt)]

    if not dates:
        return pd.NA

    earliest = min(dates)

    try:
        formatted = earliest.strftime('%Y-%m-%dT%H:%M:%S')  # ISO 8601 with T separator
    except ValueError:
        # fallback formatting if needed
        formatted = earliest.strftime('%Y-%m-%d %H:%M:%S')

    return formatted

df['earliest_date'] = df['date_times'].apply(earliest_timestamp_from_dict)

output_path = os.path.join(os.path.dirname(tbl_a), "Earliest_date.csv")
df.to_csv(output_path, index=False)

print(f"Saved earliest dates to: {output_path}")
