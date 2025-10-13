# Quick Start Guide for Send Membership Emails

## Setup Steps

1. **Configure SMTP Settings**
   ```bash
   # Edit email_config.ini with your email settings
   # For Gmail users:
   # - Enable 2-factor authentication
   # - Generate app password in Google Account settings
   # - Use app password in config file
   ```

2. **Test Email Template**
   ```bash
   # Verify email_template.txt contains your desired message
   # Template variables will be replaced with member data:
   # {anrede}, {vorname}, {nachname}, {mitgliedsnummer}, {email}
   ```

3. **Verify Data File**
   ```bash
   # Ensure ActiveMembers2025.xlsx exists and contains:
   # - RML MitglNr column
   # - Anrede, Vorname, Nachname columns  
   # - E-Mail column
   # - hash column (from prepare-data.py)
   ```

## Usage Examples

### Test Run (Recommended First Step)
```bash
# Send one test email to your own address
python send_membership_emails.py --test --test-email your-email@example.com
```

### Dry Run (Generate QR Codes Only)
```bash
# Generate QR codes without sending emails
python send_membership_emails.py --dry-run
```

### Small Batch Test
```bash
# Send emails to first 5 members only
python send_membership_emails.py --max-emails 5
```

### Full Production Run
```bash
# Send emails to all members
python send_membership_emails.py
```

## What the Script Does

1. **Reads** member data from ActiveMembers2025.xlsx
2. **Generates** personalized QR codes for each member
3. **Creates** custom email content using template
4. **Sends** emails with QR code attachments
5. **Logs** all activities and provides statistics

## Output

- **QR Codes**: Saved to `../qr-codes/` directory
- **Log File**: Timestamped log with detailed processing info
- **Statistics**: Summary of emails sent, failed, and success rate

## Important Notes

- **Always test first** with `--test` mode
- **Check email limits** with your SMTP provider
- **Monitor logs** for any errors or issues
- **Backup data** before running production batches
- **Verify hash column** exists in your data file

## Getting Help

```bash
python send_membership_emails.py --help
```