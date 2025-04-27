import csv
import html

def find_name_by_hash(csv_file_path, input_hash):
    # Open the CSV file
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        # Ensure the required columns exist
        if 'Vorname' not in reader.fieldnames or 'Nachname' not in reader.fieldnames or 'hash' not in reader.fieldnames:
            raise ValueError("The CSV file must contain 'Vorname', 'Nachname', and 'hash' columns.")

        # Iterate through each row to find a matching hash
        for row in reader:
            if row['hash'] == input_hash:
                return row['Vorname'], row['Nachname']

    # Return None if no match is found
    return None, None
def lambda_handler (event, context):
    # This function is the entry point for AWS Lambda
    # It will be triggered by an API Gateway event
    # The event contains the query string parameters passed to the API Gateway
    # read the input hash from the query string parameters
    # and call the find_name_by_hash function to check membership
    # and return the result as a HTML page

    # HTML template
    html_template = """
    <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: {background};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    font-size: 10vw;
                    font-family: Arial, sans-serif;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <center>
            {message}
            </center>
        </body>
    </html>
    """


    # Extract the hash from the query string parameters
    input_hash = event.get('queryStringParameters', {}).get('hash')

    if not input_hash:
        html_content = html_template.format(
            background="#FF0000",  # Red background for error
            title="Fehler",
            message="Ung&uuml;ltige Anfrage!"
        )
        status_code = 400  # Bad Request
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": html_content
        }
    
    # Path to your CSV file
    csv_file = './memberlist.csv'

    try:
        # Find the member by hash
        vorname, nachname = find_name_by_hash(csv_file, input_hash)

        def convert_to_html_entities(text):
            """Convert German special characters to HTML entities."""
            text = html.escape(text)  # Escape general HTML characters
            replacements = {
                'ä': '&auml;',
                'ö': '&ouml;',
                'ü': '&uuml;',
                'Ä': '&Auml;',
                'Ö': '&Ouml;',
                'Ü': '&Uuml;',
                'ß': '&szlig;'
            }
            for char, entity in replacements.items():
                text = text.replace(char, entity)
            return text

        if vorname and nachname:
            # Escape HTML characters in vorname and nachname
            vorname_safe = convert_to_html_entities(vorname)
            nachname_safe = convert_to_html_entities(nachname)
            # Return an HTML response for a valid member
            html_content = html_template.format(
                background="#00FF00",  # Green background for success
                title="Aktuelles Mitglied gefunden",
                message=f"{vorname_safe} {nachname_safe}</br>ist aktuell</br>Mitglied des RML"
            )
            status_code = 200  # OK
        else:
            # Return an HTML response for a non-member
            html_content = html_template.format(
                background="#FF0000",  # Red background for error
                title="Kein Mitglied",
                message="Kein RML-Mitglied!"
            )
            status_code = 404
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": html_content            
            }
    except Exception as e:
        # Handle any unexpected errors
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": f"<html><body><h1>Fehler</h1><p>Ein Fehler ist aufgetreten: {str(e)}</p></body></html>"
        }
    
# # Test usage
# csv_file = '../../test/memberlist.csv'  # Replace with the path to your CSV file
# input_hash = 'f647bc22205e2bca2396c8b91169eb27'  # Replace with the hash you want to search for

# vorname,nachname = find_name_by_hash(csv_file, input_hash)

# if vorname and nachname:
#     print(f"{vorname_safe} {nachname_safe} ist Mitglied im RML.")
# else:
#     print("Kein RML-Mitglied.")