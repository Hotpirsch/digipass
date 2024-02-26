from flask import Flask, request
import csv
import boto3

app = Flask(__name__)

@app.route('/membercheck')
def check_membership():
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    zipcode = request.args.get('zipcode')

    # Read the CSV file from S3 bucket
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='RML-bucket', Key='memberlist.csv')
    lines = response['Body'].read().decode('utf-8').splitlines()
    csv_reader = csv.reader(lines)

    # Check if the combination of parameters appears as a row
    for row in csv_reader:
        if row[0] == firstname and row[1] == lastname and row[2] == zipcode:
            # Generate HTML page with "Mitglied bei RML" in green color
            firstname.title()
            lastname.title()
            html = f'<html><body style="color:green">{firstname} {lastname} ist ein Mitglied der DGF Rhein-Mosel-Lahn</body></html>'
            return html

    # Generate HTML page with "Kein Mitglied" in red color
    html = '<html><body style="color:red">Kein Mitglied</body></html>'
    return html

if __name__ == '__main__':
    app.run()