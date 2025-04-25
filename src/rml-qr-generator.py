import csv
import boto3
import qrcode

# Step 1: Read the CSV file from S3 bucket
s3 = boto3.client('s3')
bucket_name = 'RML-bucket'
csv_file_name = 'memberlist.csv'
csv_file_path = f's3://{bucket_name}/{csv_file_name}'

response = s3.get_object(Bucket=bucket_name, Key=csv_file_name)
csv_data = response['Body'].read().decode('utf-8').splitlines()

# Step 2: Generate URLs and QR codes
for row in csv.reader(csv_data):
    firstname, lastname, zipcode = row

    # Generate URL
    url = f'https://example.com/membercheck?firstname={firstname}&lastname={lastname}&zipcode={zipcode}'

    # Generate QR code
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr_code = qr.make_image(fill_color="black", back_color="white")

    # Save QR code as PNG file to S3 bucket
    qr_code_file_name = f'{firstname}_{lastname}_qr.png'
    qr_code_file_path = f's3://{bucket_name}/{qr_code_file_name}'
    qr_code.save(qr_code_file_path)

    print(f'Saved QR code for {firstname} {lastname} to {qr_code_file_path}')