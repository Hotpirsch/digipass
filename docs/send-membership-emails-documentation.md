# Send Membership Emails Documentation

## Overview

The `send_membership_emails.py` script is a comprehensive Python utility that automates the process of sending personalized emails with QR code membership passes to all club members. It integrates with the existing `generate-pass.py` functionality to create individual QR codes and sends them via email with personalized messages.

## Purpose

This script automates the distribution of digital membership passes by:
- Reading member data from Excel/CSV files
- Generating personalized QR codes for each member
- Sending customized emails with QR code attachments
- Providing comprehensive logging and error handling
- Supporting test modes and batch processing options

## Features

### Email Automation
- **Bulk Email Sending**: Process all members or specific subsets
- **Personalized Content**: Template-based emails with member-specific data
- **QR Code Integration**: Generates and attaches individual QR codes
- **SMTP Support**: Compatible with Gmail, Outlook, and custom SMTP servers
- **Attachment Handling**: Professional QR code image attachments

### QR Code Generation
- **Integrated Generation**: Built-in QR code creation using generate-pass.py logic
- **Logo Embedding**: Club logo overlay on QR codes
- **Styled Design**: Green background with rounded borders
- **Dynamic Sizing**: Auto-adjusting text and layout
- **Batch Processing**: Efficient generation for multiple members

### Configuration & Control
- **Configuration File**: INI-based settings for SMTP and email parameters
- **Test Mode**: Send test emails to specific addresses
- **Dry Run Mode**: Generate QR codes without sending emails
- **Batch Limits**: Control number of emails sent in one run
- **Comprehensive Logging**: Detailed logs with timestamps and statistics

### Error Handling
- **Robust Error Recovery**: Continue processing if individual emails fail
- **Missing Data Handling**: Skip members without email addresses
- **SMTP Error Management**: Detailed error reporting for email failures
- **File System Errors**: Graceful handling of missing files or permissions

## Requirements

### Python Dependencies

Install required packages:
```bash
pip install pandas segno pillow openpyxl xlrd
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### System Requirements

- Python 3.6 or higher
- Arial font (arial.ttf) - usually pre-installed on Windows
- Internet connection for SMTP email sending
- Write permissions for QR code output directory

### Required Files

1. **Member Data File**: `ActiveMembers2025.xlsx` (or CSV equivalent)
2. **Email Template**: `email_template.txt`
3. **Club Logo**: `logo-rml3.png`
4. **Configuration**: `email_config.ini`

## Installation & Setup

### 1. Configure SMTP Settings

Edit `email_config.ini` with your email provider settings:

```ini
[SMTP]
server = smtp.gmail.com
port = 587
username = your-email@gmail.com
password = your-app-password
use_tls = True

[EMAIL]
sender_email = your-email@gmail.com
sender_name = RML e.V.
subject = Ihr neuer digitaler Mitgliedsausweis
```

### 2. Gmail App Password Setup

For Gmail users:
1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings → Security → App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password in the config file

### 3. Email Template Customization

Edit `email_template.txt` to customize the email content:
```text
Liebe/r {anrede} {vorname} {nachname},

Your personalized message here...

Mitgliedsnummer: {mitgliedsnummer}
E-Mail: {email}
```

Available template variables:
- `{anrede}` - Title (Herr/Frau)
- `{vorname}` - First name
- `{nachname}` - Last name
- `{mitgliedsnummer}` - Membership number
- `{email}` - Email address

## Usage

### Basic Usage

Send emails to all members:
```bash
python send_membership_emails.py
```

### Test Mode

Send a test email to a specific address:
```bash
python send_membership_emails.py --test --test-email your-test@email.com
```

### Dry Run Mode

Generate QR codes without sending emails:
```bash
python send_membership_emails.py --dry-run
```

### Limited Batch

Send emails to first 10 members only:
```bash
python send_membership_emails.py --max-emails 10
```

### Custom Configuration

Use a different configuration file:
```bash
python send_membership_emails.py --config my_config.ini
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--config FILE` | Specify configuration file (default: email_config.ini) |
| `--test` | Run in test mode (single email) |
| `--test-email EMAIL` | Email address for test mode |
| `--max-emails N` | Limit number of emails to send |
| `--dry-run` | Generate QR codes only, no emails |
| `--help` | Show help message |

## Configuration Reference

### SMTP Settings (`[SMTP]` section)

| Setting | Description | Example |
|---------|-------------|---------|
| `server` | SMTP server hostname | smtp.gmail.com |
| `port` | SMTP server port | 587 |
| `username` | SMTP authentication username | your-email@gmail.com |
| `password` | SMTP authentication password | app-password |
| `use_tls` | Enable TLS encryption | True |

### Email Settings (`[EMAIL]` section)

| Setting | Description | Example |
|---------|-------------|---------|
| `sender_email` | From email address | club@rml-ev.de |
| `sender_name` | Display name for sender | RML e.V. |
| `subject` | Email subject line | Ihr neuer digitaler Mitgliedsausweis |

### File Settings (`[FILES]` section)

| Setting | Description | Example |
|---------|-------------|---------|
| `excel_file` | Path to member data file | ActiveMembers2025.xlsx |
| `template_file` | Path to email template | email_template.txt |

### Popular SMTP Providers

| Provider | Server | Port | TLS |
|----------|--------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 | Yes |
| Yahoo | smtp.mail.yahoo.com | 587 | Yes |
| Custom/Corporate | your-server.com | 587/25 | Usually |

## Data Requirements

### Excel/CSV File Format

The member data file must contain these columns:
- `RML MitglNr` - Membership number (integer)
- `Anrede` - Title (Herr/Frau/etc.)
- `Vorname` - First name
- `Nachname` - Last name
- `E-Mail` - Email address
- `hash` - Unique hash value for QR code URL

### Example Data Structure
```csv
RML MitglNr;Anrede;Vorname;Nachname;E-Mail;hash
52000;Herr;John;Doe;john.doe@email.com;abc123hash
52100;Frau;Jane;Smith;jane.smith@email.com;def456hash
```

## Output & Logging

### Log Files

Each run creates a timestamped log file:
```
email_send_20251013_143022.log
```

Log entries include:
- Processing progress
- Email send confirmations
- Error messages with details
- Final statistics summary

### QR Code Files

Generated QR codes are saved to `../qr-codes/` directory with naming pattern:
```
{FirstInitial}{LastName}{MemberNumber}.png
```

Examples:
- `JDoe52000.png`
- `JSmith52100.png`

### Email Statistics

At completion, the script reports:
- Total members processed
- Members without email addresses
- QR codes successfully generated
- Emails sent successfully
- Failed email attempts
- Overall success rate

## Error Handling & Troubleshooting

### Common Issues

**SMTP Authentication Failed**
```
Solution: Verify username/password, enable app passwords for Gmail
```

**Template File Not Found**
```
Solution: Ensure email_template.txt exists in script directory
```

**Member Data File Not Found**
```
Solution: Verify Excel/CSV file path in configuration
```

**QR Code Generation Fails**
```
Solution: Check logo file (logo-rml3.png) exists and is readable
```

**Permission Denied for QR Codes**
```
Solution: Ensure write permissions for ../qr-codes/ directory
```

### SMTP Debugging

For SMTP connection issues, the script provides detailed error messages including:
- Server connection failures
- Authentication problems
- TLS/SSL certificate issues
- Timeout errors

### Test Strategies

1. **Start with Test Mode**: Always test with a single email first
2. **Use Dry Run**: Verify QR code generation before sending emails
3. **Small Batches**: Use `--max-emails 5` for initial testing
4. **Check Logs**: Review log files for detailed error information

## Security Considerations

### Email Security
- Use app passwords instead of account passwords
- Enable TLS encryption for SMTP connections
- Store credentials securely in configuration files
- Consider environment variables for sensitive data

### Data Protection
- Member email addresses are processed locally
- QR codes contain only hash values, no personal data
- Log files may contain email addresses - secure appropriately
- Clean up temporary QR code files if needed

### SMTP Rate Limiting
- Built-in 1-second delay between emails
- Respects SMTP server rate limits
- Handles temporary connection failures gracefully

## Integration with Existing System

### Relationship to Other Scripts

- **generate-pass.py**: Core QR code generation logic is integrated
- **prepare-data.py**: Generates hash values required for QR codes
- **check-membership.py**: Verification endpoint for generated QR codes

### Workflow Integration

1. **Data Preparation**: Run `prepare-data.py` to generate member hashes
2. **Email Distribution**: Run `send_membership_emails.py` to send passes
3. **Verification**: Use AWS Lambda (`check-membership.py`) for validation

### File Dependencies

```
src/
├── send_membership_emails.py    # Main email script
├── email_config.ini            # SMTP configuration
├── email_template.txt          # Email content template
├── ActiveMembers2025.xlsx      # Member database
├── logo-rml3.png              # Club logo for QR codes
└── requirements.txt           # Python dependencies

qr-codes/                      # Generated QR code directory
├── JDoe52000.png
└── ...

logs/                          # Generated log files
├── email_send_20251013_143022.log
└── ...
```

## Advanced Usage

### Batch Processing Strategies

For large member lists (500+ members):
1. Use `--max-emails` to process in smaller batches
2. Monitor SMTP provider daily limits
3. Schedule runs during off-peak hours
4. Implement retry logic for failed emails

### Custom Email Templates

Create different templates for different member types:
```bash
python send_membership_emails.py --config vorstand_config.ini
python send_membership_emails.py --config regular_config.ini
```

### Monitoring & Maintenance

- Schedule regular log file cleanup
- Monitor QR code directory size
- Track email delivery rates
- Update SMTP credentials as needed

## Version History

- **v1.0**: Initial release with basic email functionality
- **v1.1**: Added QR code integration and template system
- **v1.2**: Enhanced error handling and logging
- **Current**: Production-ready with comprehensive features

## Support & Maintenance

### Regular Maintenance Tasks
1. Update SMTP credentials when they expire
2. Clean up old log files and QR codes
3. Verify email template accuracy
4. Test with small batches before large sends

### Backup Recommendations
- Backup configuration files
- Keep copies of member data files
- Archive successful QR code generations
- Maintain log files for audit purposes

For technical support or feature requests, refer to:
- Script source code documentation
- Error logs for troubleshooting
- Configuration file comments
- Test mode for validation