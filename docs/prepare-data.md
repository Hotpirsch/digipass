# Documentation for prepare-data.py

## Overview
The `prepare-data.py` script processes a CSV file to filter and transform data for member pass validation and generation. It removes rows where the 'Austritt' column is not empty and generates a new CSV file containing the following columns:
- `RML MitglNr`
- `Vorname`
- `Nachname`
- `hash` (MD5 hash of concatenated `Vorname`, `Nachname`, and `RML MitglNr`)

## Prerequisites
- Ensure the input CSV file has the following columns:
  - `Vorname`
  - `Nachname`
  - `Austritt`
  - `RML MitglNr`
- Remove any rows above the headers in the input CSV file before running the script.

## Usage

### Input
- The script reads the input CSV file specified by the `input_csv` variable.
- The delimiter for the CSV file is `;`.

### Output
- The script generates a new CSV file specified by the `output_csv` variable.
- The output file contains the filtered rows and the additional `hash` column.

### Running the Script
1. Update the `input_csv` variable with the path to your input CSV file.
2. Update the `output_csv` variable with the desired path for the output CSV file.
3. Run the script using Python:
   ```
   python prepare-data.py
   ```

## Example
### Input CSV File (`ActiveMembers2025.csv`):
```
RML MitglNr;Vorname;Nachname;Austritt
71400;John;Doe;
52100;Jane;Smith;2025-05-31
```

### Output CSV File (`memberlist.csv`):
```
RML MitglNr,Vorname,Nachname,hash
71400,John,Doe,5d41402abc4b2a76b9719d911017c592
```

## Error Handling
- If the required columns (`Vorname`, `Nachname`, `Austritt`) are missing, the script raises a `ValueError`.

## Dependencies
- `pandas`: For reading and processing CSV files.
- `hashlib`: For generating MD5 hashes.

## Notes
- The script suppresses chained assignment warnings using `pd.options.mode.chained_assignment = None`.
- Ensure the input CSV file is properly formatted before running the script.