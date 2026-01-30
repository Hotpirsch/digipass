# digipass
Generate and validate RML membership passes
## Requirements
1. It shall be possible to validate the pass for every member of the RML.
1. It shall be possible to validate the pass outside in the field e. g. at takeoff or landing sites.
1. The pass shall be personalized.
1. The pass shall be revocable.
## Design
The pass takes the form of a QR-code that contains an URL behind which the validation takes place. The validation is completely done on the server.
## Deployment
The QR generation is done via Python on the base of an Excel export of the member list.

The QR-code validation is done by an AWS lambda function behind a function URL.

The deployment is done via Terraform.
## Operation
### Updating member data
1. The member list is exported as an Excel file from the dedicated membership management application.
1. Use Excel to export the active member list as csv. Remove any lines above the header line.
1. Use prepare-data.py to convert the csv to the format needed by the application. Remember to set the correct input file.
1. Put the `memberlist.csv` to the `/src/lambda` directory.
1. Run terraform plan/apply. from the `/deployment/terraform` directory.

### Distributing Emails
See documentation under ./docs/generate-pass-documentation.md

