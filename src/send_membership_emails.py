#!/usr/bin/env python3
"""
Email Membership Pass Script

This script sends personalized emails with QR code membership passes to all club members.
It reads member data from an Excel file, generates individual QR codes using the 
generate-pass.py functionality, and emails them to each member.

Usage:
    python send_membership_emails.py [options]

Requirements:
    - ActiveMembers2025.xlsx file with member data
    - email_template.txt file with email content
    - Logo files and fonts from generate-pass.py
    - SMTP server configuration
"""

import pandas as pd
import segno
import smtplib
import os
import sys
import logging
import hashlib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from PIL import Image, ImageDraw, ImageFont
import configparser
from pathlib import Path


class MembershipEmailSender:
    def __init__(self, config_file="email_config.ini"):
        """Initialize the email sender with configuration."""
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.setup_logging()
        self.load_config()
        
        # QR Code generation settings (from generate-pass.py)
        self.url_domain = "https://xw24b2obnym7ofrwk2ckhqktc40cglku.lambda-url.us-east-1.on.aws/"
        self.qrcode_directory = "../qr-codes"
        self.logo_path = "logo-rml3.png"
        self.font_name = "arial.ttf"
        
        # Email statistics
        self.stats = {
            'total_members': 0,
            'emails_sent': 0,
            'emails_failed': 0,
            'qr_codes_generated': 0,
            'members_without_email': 0
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_filename = f"email_send_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting email send process. Log file: {log_filename}")
    
    def load_config(self):
        """Load SMTP configuration from config file."""
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        self.config.read(self.config_file)
        
        # SMTP settings
        self.smtp_server = self.config.get('SMTP', 'server', fallback='smtp.gmail.com')
        self.smtp_port = self.config.getint('SMTP', 'port', fallback=587)
        self.smtp_username = self.config.get('SMTP', 'username', fallback='')
        self.smtp_password = self.config.get('SMTP', 'password', fallback='')
        self.smtp_use_tls = self.config.getboolean('SMTP', 'use_tls', fallback=True)
        
        # Email settings
        self.sender_email = self.config.get('EMAIL', 'sender_email', fallback=self.smtp_username)
        self.sender_name = self.config.get('EMAIL', 'sender_name', fallback='RML e.V.')
        self.subject = self.config.get('EMAIL', 'subject', fallback='Ihr neuer digitaler Mitgliedsausweis')
        
        # File paths
        self.excel_file = self.config.get('FILES', 'excel_file', fallback='ActiveMembers2025.xlsx')
        self.template_file = self.config.get('FILES', 'template_file', fallback='email_template.txt')
    
    def create_default_config(self):
        """Create a default configuration file."""
        config = configparser.ConfigParser()
        
        config['SMTP'] = {
            'server': 'smtp.gmail.com',
            'port': '587',
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'use_tls': 'True'
        }
        
        config['EMAIL'] = {
            'sender_email': 'your-email@gmail.com',
            'sender_name': 'RML e.V.',
            'subject': 'Ihr neuer digitaler Mitgliedsausweis'
        }
        
        config['FILES'] = {
            'excel_file': 'ActiveMembers2025.xlsx',
            'template_file': 'email_template.txt'
        }
        
        with open(self.config_file, 'w') as f:
            config.write(f)
        
        self.logger.warning(f"Created default config file: {self.config_file}")
        self.logger.warning("Please update the configuration with your SMTP settings!")
    
    def generate_qr_code(self, member_data):
        """Generate QR code for a single member (adapted from generate-pass.py)."""
        try:
            # Extract member information
            vorname = member_data['Vorname']
            nachname = member_data['Nachname']
            member_number = member_data['RML MitglNr']
            
            # Generate hash if not present in data
            if 'hash' in member_data and pd.notna(member_data['hash']) and member_data['hash'] != '':
                hash_value = member_data['hash']
                self.logger.debug(f"Using existing hash for {vorname} {nachname}")
            else:
                # Create MD5 hash from Vorname + Nachname + Mitgliedsnummer
                hash_input = f"{vorname}{nachname}{member_number}"
                hash_value = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
                self.logger.info(f"Generated MD5 hash for {vorname} {nachname}: {hash_value}")
            
            fname = vorname[0].upper() + nachname
            
            # Construct the URL
            url = f"{self.url_domain}?hash={hash_value}"
            
            # Generate the QR code
            qr = segno.make_qr(url, error='h')
            qr_pil = qr.to_pil(scale=5, border=3, dark='black', light='white').convert("RGB")
            
            # Load and add logo
            if os.path.exists(self.logo_path):
                logo = Image.open(self.logo_path)
                qr_pil.paste(logo, (qr_pil.size[0] // 2 - logo.size[0] // 2, 
                                   qr_pil.size[1] // 2 - logo.size[1] // 2), logo)
            
            # Create styled background
            image_width = qr_pil.size[0]
            margin = 10
            
            # Setup font
            try:
                font = ImageFont.truetype(self.font_name)
            except:
                font = ImageFont.load_default()
            
            text = f"{vorname} {nachname}"

#            # Auto-size font to fit
#            draw_temp = ImageDraw.Draw(qr_pil)
#            text_width = draw_temp.textlength(text, font=font)
#            
#            # Adjust font size to fit within margins
#            font_size = 20
#            while text_width > (image_width - 2 * margin) and font_size > 8:
#                font_size -= 1
#                try:
#                    font = ImageFont.truetype(self.font_name, font_size)
#                except:
#                    font = ImageFont.load_default()
#                text_width = draw_temp.textlength(text, font=font)
    
            # Calculate text size and ensure it fits within the image width with margins
            draw = ImageDraw.Draw(qr_pil)
            text_width = draw.textlength(text, font=font)
            while text_width > (image_width - 2 * margin):
                font = ImageFont.truetype(self.font_name, font.size - 1)  # Reduce font size
                text_width = draw.textlength(text, font=font)

            while text_width < (image_width - 2 * margin):
                font = ImageFont.truetype(self.font_name, font.size + 1)  # Increase font size
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
            os.makedirs(self.qrcode_directory, exist_ok=True)
            qr_filename = f"{self.qrcode_directory}/{fname}{member_number}.png"
            final_image.save(qr_filename, "PNG")
            
            self.stats['qr_codes_generated'] += 1
            self.logger.info(f"Generated QR code: {qr_filename}")
            
            return qr_filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate QR code for {vorname} {nachname}: {str(e)}")
            return None
    
    def load_email_template(self):
        """Load email template from file."""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"Email template file not found: {self.template_file}")
            return self.get_default_template()
        except Exception as e:
            self.logger.error(f"Error loading template: {str(e)}")
            return self.get_default_template()
    
    def get_default_template(self):
        """Return a default email template if file is not found."""
        return """Liebe/r {anrede} {vorname} {nachname},

anbei findest du deinen neuen digitalen Mitgliedsausweis als QR-Code.

Mitgliedsnummer: {mitgliedsnummer}

Mit freundlichen Grüßen
Dein RML e.V. Team"""
    
    def personalize_email(self, template, member_data):
        """Personalize email template with member data."""
        try:
            return template.format(
                anrede=member_data.get('Anrede', ''),
                vorname=member_data.get('Vorname', ''),
                nachname=member_data.get('Nachname', ''),
                mitgliedsnummer=member_data.get('RML MitglNr', ''),
                email=member_data.get('E-Mail', '')
            )
        except KeyError as e:
            self.logger.warning(f"Missing template field {e} for member {member_data.get('RML MitglNr', 'unknown')}")
            return template
    
    def send_email(self, member_data, qr_code_path):
        """Send email with QR code attachment to a member."""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = formataddr((self.sender_name, self.sender_email))
            msg['To'] = member_data['E-Mail']
            msg['Subject'] = self.subject
            
            # Load and personalize email template
            template = self.load_email_template()
            email_body = self.personalize_email(template, member_data)
            
            # Add email body
            msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            
            # Attach QR code image
            if qr_code_path and os.path.exists(qr_code_path):
                with open(qr_code_path, 'rb') as f:
                    img_data = f.read()
                
                image = MIMEImage(img_data)
                filename = f"QR_Code_{member_data['Vorname']}_{member_data['Nachname']}.png"
                image.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(image)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                # server.sendmail(self.sender_email, member_data['E-Mail'], "\n" + msg.as_string())
                server.send_message(msg)
            
            self.stats['emails_sent'] += 1
            self.logger.info(f"Email sent successfully to {member_data['E-Mail']} ({member_data['Vorname']} {member_data['Nachname']})")
            return True
            
        except Exception as e:
            self.stats['emails_failed'] += 1
            self.logger.error(f"Failed to send email to {member_data.get('E-Mail', 'unknown')}: {str(e)}")
            return False
    
    def load_member_data(self):
        """Load member data from Excel file."""
        try:
            # Try Excel file first
            if self.excel_file.endswith('.xlsx'):
                try:
                    df = pd.read_excel(self.excel_file, engine='openpyxl')
                    self.logger.info(f"Loaded {len(df)} members from Excel file: {self.excel_file}")
                except Exception:
                    # Fall back to CSV
                    csv_file = self.excel_file.replace('.xlsx', '.csv')
                    df = pd.read_csv(csv_file, sep=';')
                    self.logger.info(f"Loaded {len(df)} members from CSV file: {csv_file}")
            else:
                df = pd.read_csv(self.excel_file, sep=';')
                self.logger.info(f"Loaded {len(df)} members from CSV file: {self.excel_file}")
            
            # Filter members with email addresses
            df_with_email = df[df['E-Mail'].notna() & (df['E-Mail'] != '')]
            self.stats['total_members'] = len(df)
            self.stats['members_without_email'] = len(df) - len(df_with_email)
            
            self.logger.info(f"Members with email addresses: {len(df_with_email)}")
            self.logger.info(f"Members without email: {self.stats['members_without_email']}")
            
            return df_with_email
            
        except Exception as e:
            self.logger.error(f"Error loading member data: {str(e)}")
            return None
    
    def send_all_emails(self, test_mode=False, test_email=None, max_emails=None):
        """Send emails to all members with QR codes."""
        self.logger.info("Starting bulk email send process...")
        
        # Load member data
        df = self.load_member_data()
        if df is None:
            return False
        
        # Test mode - send only to specific email
        if test_mode and test_email:
            self.logger.info(f"TEST MODE: Sending only to {test_email}")
            # Use first member's data but override email
            if len(df) > 0:
                test_member = df.iloc[0].copy()
                test_member['E-Mail'] = test_email
                df = pd.DataFrame([test_member])
        
        # Limit number of emails if specified
        if max_emails:
            df = df.head(max_emails)
            self.logger.info(f"Limited to first {max_emails} members")
        
        success_count = 0
        
        for index, member in df.iterrows():
            try:
                self.logger.info(f"Processing member {index + 1}/{len(df)}: {member['Vorname']} {member['Nachname']}")
                
                # Generate QR code
                qr_code_path = self.generate_qr_code(member)
                
                if qr_code_path:
                    # Send email
                    if self.send_email(member, qr_code_path):
                        success_count += 1
                    
                    # Small delay to avoid overwhelming SMTP server
                    import time
                    time.sleep(1)
                else:
                    self.logger.error(f"Skipping email for {member['Vorname']} {member['Nachname']} - QR code generation failed")
                    
            except Exception as e:
                self.logger.error(f"Error processing member {member.get('RML MitglNr', 'unknown')}: {str(e)}")
                continue
        
        # Print final statistics
        self.print_statistics()
        return success_count > 0
    
    def print_statistics(self):
        """Print email sending statistics."""
        self.logger.info("=" * 50)
        self.logger.info("EMAIL SENDING STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(f"Total members in database: {self.stats['total_members']}")
        self.logger.info(f"Members without email: {self.stats['members_without_email']}")
        self.logger.info(f"QR codes generated: {self.stats['qr_codes_generated']}")
        self.logger.info(f"Emails sent successfully: {self.stats['emails_sent']}")
        self.logger.info(f"Emails failed: {self.stats['emails_failed']}")
        
        if self.stats['emails_sent'] + self.stats['emails_failed'] > 0:
            success_rate = (self.stats['emails_sent'] / (self.stats['emails_sent'] + self.stats['emails_failed'])) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        self.logger.info("=" * 50)


def main():
    """Main function with command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Send membership emails with QR codes')
    parser.add_argument('--config', default='email_config.ini', 
                       help='Configuration file path (default: email_config.ini)')
    parser.add_argument('--test', action='store_true', 
                       help='Run in test mode')
    parser.add_argument('--test-email', 
                       help='Email address for test mode')
    parser.add_argument('--max-emails', type=int, 
                       help='Maximum number of emails to send (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate QR codes but do not send emails')
    
    args = parser.parse_args()
    
    # Create email sender
    sender = MembershipEmailSender(args.config)
    
    # Validate configuration
    if not sender.smtp_username or not sender.smtp_password:
        print("ERROR: SMTP credentials not configured!")
        print(f"Please edit {args.config} with your email settings.")
        return 1
    
    if args.dry_run:
        print("DRY RUN MODE: Generating QR codes only, no emails will be sent")
        # Load data and generate QR codes only
        df = sender.load_member_data()
        if df is not None:
            for index, member in df.iterrows():
                sender.generate_qr_code(member)
        sender.print_statistics()
        return 0
    
    # Send emails
    success = sender.send_all_emails(
        test_mode=args.test, 
        test_email=args.test_email,
        max_emails=args.max_emails
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())