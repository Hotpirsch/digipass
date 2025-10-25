import asyncio
import configparser
import argparse
import hashlib
import logging
import os
import sys
import segno
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from msgraph.generated.models.file_attachment import FileAttachment
from graphmail import Graph  # Use relative import if client.py is in the same directory

# global variables
config = None
args = None
logger = None
stats = {
    'total_members': 0,
    'emails_sent': 0,
    'emails_failed': 0,
    'qr_codes_generated': 0,
    'members_without_email': 0
}
member_df = None

async def main():
    print('Python Graph Tutorial\n')
    global config
    global args
    global member_df

    # set commandline parameters
    parser = argparse.ArgumentParser(description='Send membership emails with QR codes')
    parser.add_argument('--config', default='email_config.ini', 
                       help='Configuration file path (default: email_config.ini)')
    parser.add_argument('--test-email', 
                       help='Email address for test mode')
    parser.add_argument('--max-emails', type=int, 
                       help='Maximum number of emails to send (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate QR codes but do not send emails')
    
    args = parser.parse_args()

    # Load settings
    config = configparser.ConfigParser()
    config.read([args.config, 'config.dev.cfg'])

    # Setup logging
    # setup_logging()
    # logger.info("Configuration and logging setup complete.")

    # Load member data
    member_df = load_member_data()
    if member_df is None:
        print("Failed to load member data. Exiting.")
        return
    
    # Initialize Graph client
    azure_settings = config['azure']
    client: Graph = Graph(azure_settings)

    await greet_user(client)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. Dry run (generate QR codes only)')
        print('3. Send testmail')
        print('4. Send all passes to members')
        print('5. Send pass to single member')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        try:
            if choice == 0:
                print('Goodbye...')
            elif choice == 1:
                await display_access_token(client)
            elif choice == 2:
                dry_run(client)
            elif choice == 3:
                if args.test_email:
                    mailto = args.test_email
                else:
                    mailto = input('Enter email address to send test mail to: ')
                await send_testmail(client, mailto)
            elif choice == 4:
                await send_all_passes(client)
            elif choice == 5:
                await send_pass_to_single_member(client)
            else:
                print('Invalid choice!\n')
        except ODataError as odata_error:
            print('Error:')
            if odata_error.error:
                print(odata_error.error.code, odata_error.error.message)

async def greet_user(client: Graph):
    user = await client.get_user()
    if user:
        print('Hello,', user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print('Email:', user.mail or user.user_principal_name, '\n')

async def display_access_token(client: Graph):
    token = await client.get_user_token()
    print('User token:', token, '\n')

async def send_testmail(client: Graph, mailto: str):
    global logger
    # generate QR code for test mail
    qr_code_path = generate_qr_code(member_df.iloc[0])
    message = create_message(member_df.iloc[0], qr_code_path)
    # Send mail to the specified address
    message['recipient'] = mailto
    await client.send_qr_mail(message)
    print('Mail sent to ', mailto, '\n')
    # logger.info(f"Test email sent to {mailto}")
    log_statistics()
    return 0

async def send_all_passes(client: Graph):
    global stats
    global member_df

    success_count = 0
    
    for index, member in member_df.iterrows():
        try:
            # logger.info(f"Processing member {index + 1}/{len(df)}: {member['Vorname']} {member['Nachname']}")
            
            # Generate QR code
            qr_code_path = generate_qr_code(member)
            
            if qr_code_path:
                # Send email
                message = create_message(member, qr_code_path)
                if await client.send_qr_mail(message):
                    success_count += 1
                
                # Small delay to avoid overwhelming SMTP server
                import time
                time.sleep(1)
            else:
                print(f"Skipping email for {member['Vorname']} {member['Nachname']} - QR code generation failed")
                
        except Exception as e:
            print(f"Error processing member {member.get('RML MitglNr', 'unknown')}: {str(e)}")
            continue
    
    # Log final statistics
    # log_statistics()
    return success_count > 0

async def send_pass_to_single_member(client: Graph):
    global stats
    global member_df

    membername = input('Enter member name "First Last" to send pass to: ')
    matching_rows = member_df[(member_df['Vorname'] + ' ' + member_df['Nachname']) == membername]
    if matching_rows.empty:
        print(f'No member found with name: {membername}\n')
        return
    member_data = matching_rows.iloc[0]
    qr_code_path = generate_qr_code(member_data)
    message = create_message(member_data, qr_code_path)
    await client.send_qr_mail(message)
    print(f'Pass sent to member: {membername}\n')

    stats['emails_sent'] += 1
    return

def setup_logging():
    global config
    global logger
    global stats
    #Setup logging configuration.
    log_filename = f"email_send_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("asyncio")
    logger.info(f"Starting email send process. Log file: {log_filename}")

def load_member_data():
    global config
    global logger
    global stats
    # Load member data from Excel file.
    try:
        # Try Excel file first
        excel_file = config.get('FILES', 'excel_file')
        if excel_file.endswith('.xlsx'):
            try:
                df = pd.read_excel(excel_file, engine='openpyxl')
                # logger.info(f"Loaded {len(df)} members from Excel file: {excel_file}")
            except Exception:
                # Fall back to CSV
                csv_file = excel_file.replace('.xlsx', '.csv')
                df = pd.read_csv(csv_file, sep=';')
                # logger.info(f"Loaded {len(df)} members from CSV file: {csv_file}")
        else:
            df = pd.read_csv(excel_file, sep=';')
            # logger.info(f"Loaded {len(df)} members from CSV file: {excel_file}")

        # Filter members with email addresses
        df_with_email = df[df['E-Mail'].notna() & (df['E-Mail'] != '')]
        stats['total_members'] = len(df)
        stats['members_without_email'] = len(df) - len(df_with_email)

        # logger.info(f"Members with email addresses: {len(df_with_email)}")
        # logger.info(f"Members without email: {stats['members_without_email']}")

        return df_with_email
        
    except Exception as e:
        # logger.error(f"Error loading member data: {str(e)}")
        return None

def dry_run():
    global logger
    print("DRY RUN MODE: Generating QR codes only, no emails will be sent")
    # Load data and generate QR codes only
    df = load_member_data()
    if df is not None:
        for index, member in df.iterrows():
            generate_qr_code(member)
    log_statistics()
    return 0

def log_statistics():
    global logger
    global stats
    # log email sending statistics.
    # logger.info("=" * 50)
    # logger.info("EMAIL SENDING STATISTICS")
    # logger.info("=" * 50)
    # logger.info(f"Total members in database: {stats['total_members']}")
    # logger.info(f"Members without email: {stats['members_without_email']}")
    # logger.info(f"QR codes generated: {stats['qr_codes_generated']}")
    # logger.info(f"Emails sent successfully: {stats['emails_sent']}")
    # logger.info(f"Emails failed: {stats['emails_failed']}")

    if stats['emails_sent'] + stats['emails_failed'] > 0:
        success_rate = (stats['emails_sent'] / (stats['emails_sent'] + stats['emails_failed'])) * 100
        # logger.info(f"Success rate: {success_rate:.1f}%")

    # logger.info("=" * 50)

def generate_qr_code(member_data):
    global logger
    global stats
    # Generate QR code for a single member (adapted from generate-pass.py).
    try:
        # Extract member information
        vorname = member_data['Vorname']
        nachname = member_data['Nachname']
        member_number = member_data['RML MitglNr']
        
        # Generate hash if not present in data
        if 'hash' in member_data and pd.notna(member_data['hash']) and member_data['hash'] != '':
            hash_value = member_data['hash']
            # logger.debug(f"Using existing hash for {vorname} {nachname}")
        else:
            # Create MD5 hash from Vorname + Nachname + Mitgliedsnummer
            hash_input = f"{vorname}{nachname}{member_number}"
            hash_value = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
            # logger.info(f"Generated MD5 hash for {vorname} {nachname}: {hash_value}")
        
        fname = vorname[0].upper() + nachname
        
        # Construct the URL
        url = f"{config.get('QR_CODE', 'url_domain')}?hash={hash_value}"
        
        # Generate the QR code
        qr = segno.make_qr(url, error='h')
        qr_pil = qr.to_pil(scale=5, border=3, dark='black', light='white').convert("RGB")
        
        # Load and add logo
        logo_path = config.get('QR_CODE', 'logo_path')
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            qr_pil.paste(logo, (qr_pil.size[0] // 2 - logo.size[0] // 2, 
                                qr_pil.size[1] // 2 - logo.size[1] // 2), logo)
        
        # Create styled background
        image_width = qr_pil.size[0]
        margin = 10
        
        # Setup font
        font_name = config.get('QR_CODE', 'font_name')
        font_size = 20
        try:
            font = ImageFont.truetype(font_name, size=font_size)
        except:
            print(f"Failed to load font {font_name}")
            return None
        
        text = f"{vorname} {nachname}"

        # Calculate text size and ensure it fits within the image width with margins
        draw = ImageDraw.Draw(qr_pil)
        text_width = draw.textlength(text, font=font)
        while text_width > (image_width - 2 * margin):
            font_size -= 1
            font = ImageFont.truetype(font_name, size=font_size)
            text_width = draw.textlength(text, font=font)

        while text_width < (image_width - 2 * margin):
            font_size += 1
            font = ImageFont.truetype(font_name, size=font_size)
            text_width = draw.textlength(text, font=font)
        
        # Create final image with text space
        image_height = qr_pil.size[1] + font.size + 20
        final_image = Image.new("RGB", (image_width + 2 * margin, image_height), "green")
        
        # Paste QR code
        final_image.paste(qr_pil, (margin, margin))
        
        # Add styled borders
        draw = ImageDraw.Draw(final_image)
        draw.rounded_rectangle((4, 4, final_image.size[0]-4, qr_pil.size[1]+13), 
                                outline="green", fill=None, width=7, radius=10)
        draw.rounded_rectangle((9, 9, final_image.size[0]-9, qr_pil.size[1]+9), 
                                outline="black", fill=None, width=3, radius=10)
        
        # Add member name text
        text_x = (final_image.size[0] - text_width) / 2
        text_y = qr_pil.size[1] + ((image_height - qr_pil.size[1] - font.size) / 2)
        draw.text((text_x, text_y), text, fill="white", font=font)
        
        # Save QR code
        qrcode_directory = config.get('QR_CODE', 'qrcode_directory')
        os.makedirs(qrcode_directory, exist_ok=True)
        qr_filename = f"{qrcode_directory}/{fname}{member_number}.png"
        final_image.save(qr_filename, "PNG")
        
        stats['qr_codes_generated'] += 1
        # logger.info(f"Generated QR code: {qr_filename}")

        return qr_filename
        
    except Exception as e:
        # logger.error(f"Failed to generate QR code for {vorname} {nachname}: {str(e)}")
        return None

def create_message(member_data, qr_code_path):
    global logger
    global stats
    global config
    message = {}
    # create email with QR code attachment to a member.
    try:
        # Create email message
        message['recipient'] = member_data['E-Mail']
        message['subject'] = config.get('EMAIL', 'subject')

        # Load and personalize email template
        template = load_email_template()
        email_body = personalize_email(template, member_data)

        # Add email body
        message['body'] = email_body

        # Attach QR code image
        if qr_code_path and os.path.exists(qr_code_path):
            with open(qr_code_path, 'rb') as f:
                img_data = f.read()
            
            message['qrcode'] = img_data
            filename = f"QR_Code_{member_data['Vorname']}_{member_data['Nachname']}.png"
            message['qrcode_filename'] = filename

        stats['emails_sent'] += 1
        # logger.info(f"Email created successfully for {member_data['E-Mail']} ({member_data['Vorname']} {member_data['Nachname']})")
        return message

    except Exception as e:
        stats['emails_failed'] += 1
        logger.error(f"Failed to create email for {member_data.get('E-Mail', 'unknown')}: {str(e)}")
    return False


def load_email_template():
    # Load email template from file.
    global config
    global logger
    template_file = config.get('FILES', 'template_file')
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Email template file not found: {template_file}")
        return None
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        return None

def personalize_email(template, member_data):
    global logger
    # Personalize email template with member data.
    try:
        return template.format(
            anrede=member_data.get('Anrede', ''),
            vorname=member_data.get('Vorname', ''),
            nachname=member_data.get('Nachname', ''),
            mitgliedsnummer=member_data.get('RML MitglNr', ''),
            email=member_data.get('E-Mail', '')
        )
    except KeyError as e:
        logger.warning(f"Missing template field {e} for member {member_data.get('RML MitglNr', 'unknown')}")
        return template

# Run main
asyncio.run(main())