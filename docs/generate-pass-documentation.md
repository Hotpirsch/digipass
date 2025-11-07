# Generate Pass Documentation

## Overview

The digital membership pass system consists of two main components:

1. **`generate-pass.py`**: A Python utility that generates QR code-based digital membership passes for club members. It creates visually appealing QR codes with embedded logos and member information.

2. **`azure-mailtest.py`**: An automated email distribution system that generates and sends personalized QR code passes directly to members via Microsoft Graph API (Azure).

## Purpose

This system is designed to create and distribute digital membership passes that:
- Generate QR codes containing secure URLs with member hash values
- Include the club logo embedded within the QR code
- Display member names below the QR code
- Save individual pass images for distribution to members
- Automatically send personalized passes via email to all members
- Provide secure membership verification through hash-based URLs

## Features

- **QR Code Generation**: Creates high-quality QR codes with error correction
- **Logo Integration**: Embeds the club logo in the center of each QR code
- **Custom Styling**: Applies green background with rounded borders for visual appeal
- **Dynamic Text Sizing**: Automatically adjusts font size to fit member names
- **Batch Processing**: Processes multiple members from a membership list file
- **Error Handling**: Robust error handling for missing members or invalid data

## Requirements

### Dependencies

The scripts require the following Python packages (see `requirements.txt`):

**Core Dependencies (for `generate-pass.py`):**
```
pandas
segno
pillow
```

**Additional Dependencies (for `azure-mailtest.py`):**
```
msgraph-core
azure-identity
asyncio
configparser
```

### System Requirements

- Python 3.6 or higher
- Open Sans Serif font (OpenSans-Medium.ttf) coming with the repo
- Club logo image file (`logo-rml3.png`) coming with the repo

### Input Files

1. **Membership Numbers File**: A text file containing member numbers (one per line)
   - Example: `vorstand.list`
   - Format: Plain text with one membership number per line

2. **Member Data CSV**: A semicolon-separated CSV file with member information
   - Example: `ActiveMembers2025.csv`
   - Required columns:
     - `RML MitglNr`: Member number (integer)
     - `Vorname`: First name
     - `Nachname`: Last name
     - `hash`: Unique hash value for URL generation

## Usage

### Command Line Syntax

```bash
python generate-pass.py <membership_number_file> <csv_file>
```

### Parameters

- `membership_number_file`: Path to the text file containing membership numbers
- `csv_file`: Path to the CSV file containing member data

### Example

```bash
python generate-pass.py member.list ActiveMembers2025.csv
```

This command will:
1. Read membership numbers from `member.list`
2. Look up member data in `ActiveMembers2025.csv`
3. Generate QR code passes for each member
4. Save images to the `../qr-codes/` directory

## Configuration

### URL Domain

The script uses a function URL for generating QR code links:

```python
url_domain = "https://<function-url>/"
```

**To customize**: Update the `url_domain` variable with your verification service URL.

### Output Directory

QR codes are saved to:

```python
qrcode_directory = "../qr-codes"
```

**To customize**: Modify the `qrcode_directory` variable to change the output location.

### Visual Styling

The script creates passes with:
- **QR Code**: High error correction, 5x scale, 3-pixel border
- **Background**: Green color with rounded corners
- **Borders**: Green outer border (7px width) and black inner border (3px width)
- **Logo**: Centered overlay on the QR code
- **Text**: White color, Arial font, auto-sized to fit

## Output

### File Naming Convention

Generated files are named using the pattern:
```
{FirstInitial}{LastName}{MemberNumber}.png
```

Examples:
- `FKrüger12345.png` (Freddy Krüger, Member #12345)
- `JCena54321.png` (John Cena, Member #54321)

### Image Specifications

- **Format**: PNG
- **Color Mode**: RGB
- **Dimensions**: Variable (based on QR code size + margins)
- **Background**: Green with rounded borders
- **QR Code**: High-resolution with embedded logo
- **Text**: Member's full name below QR code

## Functions

### `nice_qr_code(matching_row)`

Generates a styled QR code pass for a single member.

**Parameters:**
- `matching_row`: Pandas DataFrame row containing member data

**Process:**
1. Extracts member information (name, hash, member number)
2. Constructs verification URL with hash parameter
3. Generates QR code with high error correction
4. Adds club logo overlay
5. Creates styled background with borders
6. Adds member name text
7. Saves final image

### `generate_qr_codes_from_file(input_file, csv_file_path)`

Processes multiple members from input files.

**Parameters:**
- `input_file`: Path to membership numbers file
- `csv_file_path`: Path to member data CSV

**Process:**
1. Reads membership numbers from input file
2. Loads member data from CSV
3. Validates required columns exist
4. Processes each membership number
5. Generates QR code for each valid member
6. Handles errors for missing or invalid members

### Hash-Based URLs

The script generates URLs containing unique hash values for each member:
```
https://domain.com/?hash={unique_hash}
```

**Security Features:**
- Each member has a unique hash for verification
- Hash values are pre-generated and stored securely
- URLs point to a verification service (Lambda function)

### Data Protection

- Member data is processed locally
- No sensitive information is embedded in QR codes
- Hash values provide secure, anonymous verification

## Integration

### Verification Service

The generated QR codes link to a verification service that:
- Accepts hash parameters via GET requests
- Validates membership status
- Returns verification results

## Troubleshooting

### Common Issues

**Font Not Found**
```
Solution: Ensure arial.ttf is installed or update font path
```

**Logo Image Missing**
```
Solution: Verify logo-rml3.png exists in the script directory
```

**Member Not Found**
```
Solution: Check membership number format and CSV data
```

**Permission Denied**
```
Solution: Ensure write permissions for output directory
```

### Debug Steps

1. Verify all input files exist and are readable
2. Check CSV column names match requirements
3. Ensure output directory exists and is writable
4. Validate membership numbers format (integers)
5. Test with a single member first

## File Structure

```
src/
├── generate-pass.py          # Main QR code generation script
├── azure-mailtest.py         # Email distribution system
├── graphmail.py              # Microsoft Graph API client
├── requirements.txt          # Python dependencies
├── email_config.ini          # Email system configuration
├── email_template.txt        # Email template with placeholders
├── logo-rml3.png            # Club logo image
├── OpenSans-Medium.ttf       # Font file for QR codes
├── ActiveMembers2025.csv    # Member database
├── vorstand.list            # Membership numbers
└── arial.ttf                # Alternative font file (system)

qr-codes/
├── FKrüger12345.png         # Generated passes
├── JCena54321.png
└── ...
```

## Version History

- **Current Version**: Production release for 2025 membership year
- **Features Added**: Logo embedding, styled borders, auto-sizing text
- **Dependencies**: Updated to use segno for QR generation

## Related Scripts

- `prepare-data.py`: Generates member hashes and prepares CSV data
- `check-membership.py`: Lambda function for membership verification
- `azure-mailtest.py`: Automated email distribution system for membership passes

### Azure Mail Distribution (`azure-mailtest.py`)

The `azure-mailtest.py` script provides an automated email distribution system that generates QR code passes and sends them directly to members via Microsoft Graph API (Azure).

#### Features

- **Automated Email Distribution**: Sends personalized emails with QR code attachments to all members
- **Microsoft Graph Integration**: Uses Azure Active Directory for secure email sending
- **QR Code Generation**: Integrates the same QR code generation logic as `generate-pass.py`
- **Batch Processing**: Processes multiple members with progress tracking and statistics
- **Test Mode Support**: Allows testing with specific email addresses before bulk sending
- **Configuration Management**: Uses INI files for flexible configuration

#### Requirements

**Additional Dependencies for Email Distribution:**
```
msgraph-core
azure-identity
asyncio
```

**Azure Configuration:**
- Azure AD application registration
- Microsoft Graph API permissions: `User.Read`, `Mail.Send`, `Mail.Read`
- Valid tenant ID and client ID

#### Usage

**Interactive Mode:**
```bash
python azure-mailtest.py
```

**Command Line Options:**
```bash
python azure-mailtest.py --config email_config.ini --test-email test@example.com --max-emails 5 --dry-run
```

**Available Parameters:**
- `--config`: Configuration file path (default: `email_config.ini`)
- `--test-email`: Email address for test mode
- `--max-emails`: Maximum number of emails to send (for testing)
- `--dry-run`: Generate QR codes without sending emails

#### Interactive Menu Options

1. **Display Access Token**: Shows current Azure authentication token
2. **Dry Run**: Generate QR codes only without sending emails
3. **Send Test Mail**: Send a test email to specified address
4. **Send All Passes**: Send passes to all members with email addresses
5. **Send Pass to Single Member**: Send pass to specific member by name

#### Configuration (`email_config.ini`)

The script uses a comprehensive configuration file with the following sections:

**Azure Settings:**
```ini
[azure]
clientId = your-azure-client-id
tenantId = your-azure-tenant-id
graphUserScopes = User.Read Mail.Send Mail.Read
```

**QR Code Settings:**
```ini
[QR_CODE]
url_domain = https://your-verification-service.com/
qrcode_directory = ../qr-codes
logo_path = logo-rml3.png
font_name = ./OpenSans-Medium.ttf
```

**File Paths:**
```ini
[FILES]
excel_file = ActiveMembers2025.csv
template_file = email_template.txt
```

**Email Configuration:**
```ini
[EMAIL]
subject = Dein neuer digitaler Mitgliedsausweis
```

#### Email Template (`email_template.txt`)

The script uses a customizable email template with placeholder variables:
- `{vorname}`: Member's first name
- `{nachname}`: Member's last name
- `{mitgliedsnummer}`: Member number
- `{email}`: Member's email address

#### Statistics and Monitoring

The script tracks and reports:
- Total members processed
- QR codes generated successfully
- Emails sent successfully
- Emails failed
- Members without email addresses
- Success rate percentage

#### Security Features

- **Hash Generation**: Automatic MD5 hash creation if not present in member data
- **Secure Authentication**: Uses Microsoft Graph API with OAuth2
- **Email Validation**: Processes only members with valid email addresses
- **Error Handling**: Robust error handling for network and authentication issues

#### Integration with Generate Pass Workflow

The `azure-mailtest.py` script integrates seamlessly with the existing pass generation workflow:

1. **Data Source**: Uses the same `ActiveMembers2025.csv` file as `generate-pass.py`
2. **QR Code Generation**: Implements identical QR code styling and generation logic
3. **Hash Management**: Supports both pre-generated hashes and on-the-fly MD5 generation
4. **File Naming**: Uses the same naming convention for generated QR code files

#### Best Practices

- **Test First**: Always use dry-run or test-email modes before bulk sending
- **Monitor Statistics**: Review email statistics for failed deliveries
- **Batch Limits**: Use `--max-emails` parameter for testing with limited batches
- **Error Recovery**: Check logs for failed emails and retry if necessary

#### Operations

1. Run `python azure-mailtest.py` in a virtual Python environment (venv).
2. Follow the steps announced by the script. Use the URL and code to log in to a thermik4u user account.
3. Select one of the options displayed by the script.
4. When you are done, select `0` to exit the script.