import database
from exif import Image as ExifImage
import os
from PIL import Image
from io import BytesIO
from postmarker.core import PostmarkClient

# Initialize Postmark client
POSTMARK_API_TOKEN = os.getenv('POSTMARK_API_TOKEN')
postmark = PostmarkClient(server_token=POSTMARK_API_TOKEN)

# Get geo info from image
def get_geo_info(image_data):
    """
    Extracts GPS information from an image.
    
    Args:
        image_data: bytes - The image data to extract GPS information from.
        
    Returns:	
        dict - A dictionary containing the GPS information if found, otherwise None.
    """

    try:
        # Create a BytesIO object from the image data
        image_stream = BytesIO(image_data)
        
        # Open the image with PIL
        image = Image.open(image_stream)
        
        # Check if the image has EXIF data
        if not image._getexif():
            return None
        
        # Create an ExifImage object
        exif_image = ExifImage(image_data)
        
        # Extract GPS information
        if exif_image.has_exif:
            try:
                # Get GPS info
                gps_latitude = exif_image.gps_latitude
                gps_longitude = exif_image.gps_longitude
                gps_altitude = exif_image.gps_altitude
                
                # Convert to decimal degrees
                lat = gps_latitude[0] + gps_latitude[1]/60 + gps_latitude[2]/3600
                lon = gps_longitude[0] + gps_longitude[1]/60 + gps_longitude[2]/3600
                
                # Adjust for N/S and E/W
                if exif_image.gps_latitude_ref == 'S':
                    lat = -lat
                if exif_image.gps_longitude_ref == 'W':
                    lon = -lon
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': gps_altitude
                }
            except (AttributeError, TypeError):
                return None
    except Exception:
        return None
    
    return None


# Send confirmation email
def send_confirmation_email(email_data, submission_hash):
    """
    Send a confirmation email to the submitter using Postmark.
    
    Args:
        email_data (dict): The original email data containing sender information
        submission_hash (str): The unique hash of the submission
    """
    try:
        # Prepare email content
        subject = f"Submission Received - {submission_hash}"
        
        # Create HTML content
        html_body = f"""
        <html>
            <body>
                <h2>Thank you for your submission!</h2>
                <p>We have received your environmental monitoring submission with ID: <strong>{submission_hash}</strong></p>
                <p>Your data has been successfully processed and stored in our system.</p>
                <hr>
                <p><small>This is an automated response. Please do not reply to this email.</small></p>
            </body>
        </html>
        """
        
        # Create plain text content
        text_body = f"""
        Thank you for your submission!
        
        We have received your environmental monitoring submission with ID: {submission_hash}
        
        Your data has been successfully processed and stored in our system.
        
        ---
        This is an automated response. Please do not reply to this email.
        """
        
        # Send email using Postmark
        postmark.emails.send(
            From='developer@developer-service.io',
            To=email_data['from_email'],
            Subject=subject,
            HtmlBody=html_body,
            TextBody=text_body,
            MessageStream='outbound'
        )
        
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        return False


# Save email and attachments
def save_email_and_attachments(email_data, attachments):
    # Save email and get its ID
    email_id, submission_hash = database.save_email(email_data)

    # Save attachments
    for attachment in attachments:
        # Add email_id to attachment
        attachment['email_id'] = email_id

        # Save attachment
        attachment_id = database.save_attachment(attachment)

        # Save image to disk
        attachment_content = attachment['content']
        with open(f"static/attachments/{attachment_id}", "wb") as f:
            f.write(attachment_content)

    # Send confirmation email
    send_confirmation_email(email_data, submission_hash)

    # Return email ID
    return email_id
