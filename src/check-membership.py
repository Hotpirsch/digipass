import pandas as pd

def find_name_by_hash(csv_file_path, input_hash):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the required columns exist
    if 'Vorname' not in df.columns or 'Nachname' not in df.columns or 'hash' not in df.columns:
        raise ValueError("The CSV file must contain 'Vorname', 'Nachname', and 'hash' columns.")

    # Find the row where the 'hash' column matches the input hash
    matching_row = df[df['hash'] == input_hash]

    # If a matching row is found, return the 'Vorname' and 'Nachname' values
    if not matching_row.empty:
        vorname = matching_row.iloc[0]['Vorname']
        nachname = matching_row.iloc[0]['Nachname']
        return vorname, nachname

    # Return None if no match is found
    return None,None

# Example usage
csv_file = '../test/memberlist.csv'  # Replace with the path to your CSV file
input_hash = '1e7455a47d9fec6ed988e7a0cdf31d40'  # Replace with the hash you want to search for

vorname,nachname = find_name_by_hash(csv_file, input_hash)
if vorname and nachname:
    print(f"{vorname} {nachname} ist Mitglied im RML.")
else:
    print("Kein RML-Mitglied.")