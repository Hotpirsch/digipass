import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont

url_domain = "https://xw24b2obnym7ofrwk2ckhqktc40cglku.lambda-url.us-east-1.on.aws/"  # Replace with your actual domain

def generate_member_qr(member_number, csv_file_path, output_png_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the required columns exist
    if 'RML MitglNr' not in df.columns or 'Vorname' not in df.columns or 'Nachname' not in df.columns or 'hash' not in df.columns:
        raise ValueError("The CSV file must contain 'RML MitglNr', 'Vorname', 'Nachname', and 'hash' columns.")

    # Find the row where the member number matches
    matching_row = df[df['RML MitglNr'] == member_number]

    if matching_row.empty:
        raise ValueError(f"No member found with member number {member_number}.")

    # Extract the required values
    vorname = matching_row.iloc[0]['Vorname']
    nachname = matching_row.iloc[0]['Nachname']
    hash_value = matching_row.iloc[0]['hash']

    # Construct the URL
    url = f"{url_domain}?hash={hash_value}"

    # Generate the QR code
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Create a blank image to embed the QR code and text
    image_width = qr_image.size[0]
    margin = 15
    font = ImageFont.truetype("DejaVuSans.ttf")  # Use ttf font
    text = f"{vorname} {nachname}"

    # Calculate text size and ensure it fits within the image width with margins
    draw = ImageDraw.Draw(qr_image)
    text_width = draw.textlength(text, font=font)
    while text_width > (image_width - 2 * margin):
        font = ImageFont.truetype("DejaVuSans.ttf", font.size - 1)  # Reduce font size
        text_width = draw.textlength(text, font=font)

    while text_width < (image_width - 2 * margin):
        font = ImageFont.truetype("DejaVuSans.ttf", font.size + 1)  # Increase font size
        text_width = draw.textlength(text, font=font)

    # Create a new image with space for the text
    image_height = qr_image.size[1] + font.size + 20  # Add space for text
    final_image = Image.new("RGB", (image_width, image_height), "green")

    # Paste the QR code onto the blank image
    final_image.paste(qr_image, (0, 0))

    # Add text below the QR code
    draw = ImageDraw.Draw(final_image)
    text_x = (image_width - text_width) // 2
    text_y = qr_image.size[1] + ((image_height - qr_image.size[1] - font.size) / 2 )  # Position text below the QR code
    draw.text((text_x, text_y), text, fill="white", font=font)

    # Save the final image as a PNG
    final_image.save(output_png_path)
    print(f"QR code PNG saved to {output_png_path}")

# Example usage
csv_file = './lambda/memberlist.csv'  # Path to your CSV file
member_number = 71400  # Replace with the desired member number
output_png = 'member_qr.png'  # Path to save the generated PNG

generate_member_qr(member_number, csv_file, output_png)