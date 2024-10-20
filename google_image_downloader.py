from flask import Flask, request, render_template
from google_images_download import google_images_download
import os
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# Initialize google_images_download
response = google_images_download.googleimagesdownload()

# Function to download images
def download_images(keyword, num_images):
    arguments = {
        "keywords": keyword,
        "limit": num_images,
        "print_urls": True,
        "format": "jpg",
        "output_directory": "downloads",
        "no_directory": True  # Prevent creating a subfolder per keyword
    }
    paths = response.download(arguments)
    return paths

# Function to zip the downloaded images
def create_zip_file(folder, zip_filename):
    zip_path = os.path.join(folder, zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".jpg"):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.basename(file_path))
    return zip_path

# Function to send email with the ZIP file
def send_email(recipient_email, zip_file_path):
    sender_email = 'ssoumya_be22@thapar.edu'  # Replace with your email
    sender_password = 'Sjindal_13'      # Replace with your email password

    # Set up the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Your Downloaded Images'

    # Attach the ZIP file
    part = MIMEBase('application', 'octet-stream')
    with open(zip_file_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(zip_file_path)}')
    msg.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Route for the homepage
@app.route('/')
def index():
    return render_template('gid.html')

# Route for handling form submission
@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        keyword = request.form['keyword']
        num_images = int(request.form['numImages'])
        recipient_email = request.form['email']
        print(request.form)
        # Download images
        download_images(keyword, num_images)
        
        # Zip the downloaded images
        zip_file = create_zip_file('downloads', f"{keyword}_images.zip")
        
        # Send the ZIP file via email
        send_email(recipient_email, zip_file)

        return f"Downloaded {num_images} images and sent them to {recipient_email}"

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)


