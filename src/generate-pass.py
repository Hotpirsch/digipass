import pandas as pd
import segno
from PIL import Image, ImageDraw, ImageFont, ImagePath
import sys

url_domain = "https://xw24b2obnym7ofrwk2ckhqktc40cglku.lambda-url.us-east-1.on.aws/"  # Replace with your actual domain
qrcode_directory = "../qr-codes"  # Directory where the QR-codes are stored

def nice_qr_code(matching_row):
    font_name = "OpenSans-Medium.ttf"  # Path to your TTF font file
    logo = Image.open("logo-rml3.png")  # Path to your logo image

    # Extract the required values
    vorname = matching_row.iloc[0]['Vorname']
    nachname = matching_row.iloc[0]['Nachname']
    hash_value = matching_row.iloc[0]['hash']
    member_number = matching_row.iloc[0]['RML MitglNr']
    fname = vorname[0].upper() + nachname

    # Construct the URL
    url = f"{url_domain}?hash={hash_value}"

    # Generate the QR code
    qr = segno.make_qr(url,error='h')
    qr_pil = qr.to_pil(scale=5, border=3, dark='black', light='white').convert("RGB")
    # Add logo to the QR code
    qr_pil.paste(logo, (qr_pil.size[0] // 2 - logo.size[0] // 2, qr_pil.size[1] // 2 - logo.size[1] // 2), logo)

    # Create a blank image to embed the QR code and text
    image_width = qr_pil.size[0]
    margin = 10
    font = ImageFont.truetype(font_name)  # Use ttf font
    text = f"{vorname} {nachname}"

    # Calculate text size and ensure it fits within the image width with margins
    draw = ImageDraw.Draw(qr_pil)
    text_width = font.getbbox(text)[2]
    while text_width > (image_width - 2 * margin):
        font = ImageFont.truetype(font_name, font.size - 1)  # Reduce font size
        text_width = font.getbbox(text)[2]

    while text_width < (image_width - 2 * margin):
        font = ImageFont.truetype(font_name, font.size + 1)  # Increase font size
        text_width = font.getbbox(text)[2]

    # Create a new image with space for the text
    text_height = font.getbbox(text)[3]
    image_height = qr_pil.size[1] + text_height + 20  # Add space for text
    final_image = Image.new("RGB", (image_width + 2 * margin, image_height), "green")

    # Paste the QR code onto the blank image
    final_image.paste(qr_pil, (margin, margin))
    draw = ImageDraw.Draw(final_image)
    draw.rounded_rectangle((4, 4, final_image.size[0]-4, qr_pil.size[1]+13), outline="green", fill=None, width=7, radius=10)
    draw.rounded_rectangle((9, 9, final_image.size[0]-9, qr_pil.size[1]+9), outline="black", fill=None, width=3, radius=10)

    # Add text below the QR code
    draw = ImageDraw.Draw(final_image)
    text_x = (final_image.size[0] - text_width) / 2
    text_y = qr_pil.size[1] + (image_height - qr_pil.size[1] - text_height - 10 )  # Position text below the QR code
    draw.text((text_x, text_y), text, fill="white", font=font)

    final_image.save(f"{qrcode_directory}/{fname}{member_number}.png", "PNG")

def generate_qr_codes_from_file(input_file, csv_file_path):
    """
    Reads a file containing membership numbers and generates QR codes for each member.

    :param input_file: Path to the file containing membership numbers.
    :param csv_file_path: Path to the CSV file containing member data.
    """
    try:
        # Open the membership numbers input file
        with open(input_file, 'r') as file:
            membership_numbers = [line.strip() for line in file.readlines()]

        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Ensure the required columns exist
        if 'RML MitglNr' not in df.columns or 'Vorname' not in df.columns or 'Nachname' not in df.columns or 'hash' not in df.columns:
            raise ValueError("The CSV file must contain 'RML MitglNr', 'Vorname', 'Nachname', and 'hash' columns.")

        for member_number in membership_numbers:
            try:
                # Find the row where the member number matches
                matching_row = df[df['RML MitglNr'] == int(member_number)]

                if matching_row.empty:
                    raise ValueError(f"No member found with member number {member_number}.")

                nice_qr_code(matching_row)
                print(f"QR code generated for member number: {member_number}")
            except ValueError as e:
                print(f"Error generating QR code for member number {member_number}: {e}")
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate-pass.py <membership_number_file> <csv_file>")
        sys.exit(1)
    else:
        print("Generating QR codes...")

    input_file = sys.argv[1]
    csv_file = sys.argv[2]

    generate_qr_codes_from_file(input_file, csv_file)