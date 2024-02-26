from flask import Flask, request, render_template
import csv

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
        background = "red"
        
        # read the CSV file from the local file system
        with open('./memberlist.csv') as csvfile:
            csv_reader = csv.reader(csvfile)
            # Check if the combination of parameters appears as a row
            for row in csv_reader:
                if row[0] == firstname.lower() and row[1] == lastname.lower() and row[2] == zipcode:
                    background = "green"

        return render_template("member.html", firstname=firstname, lastname=lastname, background=background)

    return app
