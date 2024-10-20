from flask import Flask, request, render_template
from icrawler import ImageDownloader
from icrawler.builtin import GoogleImageCrawler
import os
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import shutil
import traceback

app = Flask(__name__)

# Function to download images using iCrawler
def download_images(keyword, num_images):
    # Define the output directory
    output_directory = 'downloads'
    
    # Make sure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Create a BingImageCrawler object
    crawler = GoogleImageCrawler(storage={'root_dir': output_directory})

    try:
        # Download images
        crawler.crawl(keyword=keyword, max_num=num_images)
        print(f"Downloaded images for keyword: {keyword}")
        
        # Return the list of downloaded images
        return os.listdir(output_directory)  
    except Exception as e:
        print(f"Error downloading images: {e}")
        traceback.print_exc()
        return None

# Function to zip the downloaded images
def create_zip_file(folder, zip_filename):
    zip_path = os.path.join(folder, zip_filename)
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".jpg") or file.endswith(".png"):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.basename(file_path))
        return zip_path
    except Exception as e:
        print(f"Error creating zip file: {e}")
        traceback.print_exc()
        return None

# Function to send email with the ZIP file
def send_email(recipient_email, zip_file_path):
    try:
        sender_email = "ssoumya_be22@thapar.edu"  # Change to your email
        sender_password = "Sjindal_13"  # Change to your password

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
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        traceback.print_exc()

# Function to clean up the download directory after zipping
def cleanup_downloads(folder):
    try:
        shutil.rmtree(folder)
        print(f"Cleanup successful: {folder} deleted.")
    except Exception as e:
        print(f"Error cleaning up downloads: {e}")
        traceback.print_exc()

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

        print(f"Form received: {request.form}")

        # Step 1: Download images
        download_results = download_images(keyword, num_images)
        if not download_results:
            return "Error downloading images. No images found for the specified keyword."

        # Step 2: Zip the downloaded images
        zip_file = create_zip_file('downloads', f"{keyword}_images.zip")
        if not zip_file:
            return "Error creating zip file. Please try again."

        # Step 3: Send the ZIP file via email
        send_email(recipient_email, zip_file)

        # Step 4: Cleanup downloaded files
        cleanup_downloads('downloads')

        return f"Downloaded {len(download_results)} images and sent them to {recipient_email}"

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

