# This script reads a CSV file. Remove any rows above the headers before running this script.
# It filters the rows where the 'Austritt' column is empty and generates a new CSV file with 'name',
# 'firstname', and an additional 'hash' column.
# The output serves as the base data for the member pass validation and generation.

import pandas as pd
import hashlib

pd.options.mode.chained_assignment = None  # default='warn'

def filter_and_generate_csv(input_csv_path, output_csv_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_path,delimiter=';')

    # Ensure the required columns exist
    if 'Vorname' not in df.columns or 'Nachname' not in df.columns or 'Austritt' not in df.columns:
        raise ValueError("The input CSV file must contain 'Vorname', 'Nachname', and 'Austritt' columns.")

    # Filter rows where 'Austritt' is empty
    filtered_df = df[df['Austritt'].isna()]

    # Create a new column with the MD5 hash of concatenated 'Vorname' and 'Nachname' and 'RML MitglNr'
    def generate_md5(row):
        concatenated = f"{row['Vorname']}{row['Nachname']}{row['RML MitglNr']}"
        return hashlib.md5(concatenated.encode('utf-8')).hexdigest()

    filtered_df['hash'] = filtered_df.apply(generate_md5, axis=1)

    # Select only the required columns for the output
    output_df = filtered_df[['RML MitglNr', 'Vorname', 'Nachname', 'hash']]

    # Write the output to a CSV file
    output_df.to_csv(output_csv_path, index=False)

    print(f"Filtered CSV file with hashes has been saved to {output_csv_path}")

input_csv = 'ActiveMembers202601.csv'  # Replace with the path to your input CSV file
output_csv = 'memberlist.csv'  # Replace with the desired output CSV file path

filter_and_generate_csv(input_csv, output_csv)