import database
from exif import Image as ExifImage


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
        from PIL import Image
        from io import BytesIO
        
        # Open image from bytes
        image = Image.open(BytesIO(image_data))
        
        # Try to get EXIF data
        try:
            exif_image = ExifImage(image_data)
            if exif_image.has_exif:
                # Get GPS info
                if hasattr(exif_image, 'gps_latitude') and hasattr(exif_image, 'gps_longitude'):
                    lat = exif_image.gps_latitude
                    lon = exif_image.gps_longitude
                    alt = exif_image.gps_altitude if hasattr(exif_image, 'gps_altitude') else None
                    
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "altitude": alt
                    }
        except Exception as e:
            print(f"Error extracting EXIF data: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
    
    return None


# Save email and attachments
def save_email_and_attachments(email_data, attachments):
    # Save email and get its ID
    email_id = database.save_email(email_data)

    # Save attachments
    for attachment in attachments:
        # Add email_id to attachment
        attachment['email_id'] = email_id

        # Save attachment
        attachment_id = database.save_attachment(attachment)

        # Save image to disk
        attachment_name = attachment['name']
        attachment_content = attachment['content']
        with open(f"static/attachments/{attachment_id}", "wb") as f:
            f.write(attachment_content)

    # Return email ID
    return email_id
