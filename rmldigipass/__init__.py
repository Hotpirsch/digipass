from flask import Flask, request
import csv
import boto3
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/membercheck', methods=['GET'])  
    def membercheck():
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        zipcode = request.args.get('zipcode')

        # # Read the CSV file from S3 bucket
        # s3 = boto3.client('s3')
        # response = s3.get_object(Bucket='RML-bucket', Key='memberlist.csv')
        # lines = response['Body'].read().decode('utf-8').splitlines()
        # csv_reader = csv.reader(lines)

        # # Check if the combination of parameters appears as a row
        # for row in csv_reader:
        #     if row[0] == firstname and row[1] == lastname and row[2] == zipcode:
        #         # Generate HTML page with "Mitglied bei RML" in green color
        #         firstname.title()
        #         lastname.title()
        #         html = f'<html><body style="color:green">{firstname} {lastname} ist ein Mitglied der DGF Rhein-Mosel-Lahn</body></html>'
        #         return html

        # # Generate HTML page with "Kein Mitglied" in red color
        # html = '<html><body style="color:red">Kein Mitglied</body></html>'
        html = f'<html><body style="color:green">{firstname} {lastname} ist ein Mitglied der DGF Rhein-Mosel-Lahn</body></html>'
        return html

    return app
