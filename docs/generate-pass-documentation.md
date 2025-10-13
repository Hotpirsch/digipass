# Generate Pass Documentation

## Overview

The `generate-pass.py` script is a Python utility that generates QR code-based digital membership passes for club members. It creates visually appealing QR codes with embedded logos and member information that can be used for digital verification systems.

## Purpose

This script is designed to create digital membership passes that:
- Generate QR codes containing secure URLs with member hash values
- Include the club logo embedded within the QR code
- Display member names below the QR code
- Save individual pass images for distribution to members

## Features

- **QR Code Generation**: Creates high-quality QR codes with error correction
- **Logo Integration**: Embeds the club logo in the center of each QR code
- **Custom Styling**: Applies green background with rounded borders for visual appeal
- **Dynamic Text Sizing**: Automatically adjusts font size to fit member names
- **Batch Processing**: Processes multiple members from a membership list file
- **Error Handling**: Robust error handling for missing members or invalid data

## Requirements

### Dependencies

The script requires the following Python packages (see `requirements.txt`):

```
pandas
segno
pillow
```

### System Requirements

- Python 3.6 or higher
- Arial font (arial.ttf) installed on the system
- Club logo image file (`logo-rml3.png`)

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
├── generate-pass.py          # Main script
├── requirements.txt          # Python dependencies
├── logo-rml3.png            # Club logo image
├── ActiveMembers2025.csv    # Member database
├── vorstand.list            # Membership numbers
└── arial.ttf                # Font file (system)

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
