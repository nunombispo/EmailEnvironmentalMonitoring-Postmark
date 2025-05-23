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
        # Try to get EXIF data
        exif_image = ExifImage(image_data)
        
        if not exif_image.has_exif:
            return None
            
        # Extract GPS information
        if hasattr(exif_image, 'gps_latitude') and hasattr(exif_image, 'gps_longitude'):
            lat = exif_image.gps_latitude
            lon = exif_image.gps_longitude
            
            # Convert to decimal degrees
            lat_decimal = lat[0] + lat[1]/60 + lat[2]/3600
            lon_decimal = lon[0] + lon[1]/60 + lon[2]/3600
            
            # Adjust for South/West
            if exif_image.gps_latitude_ref == 'S':
                lat_decimal = -lat_decimal
            if exif_image.gps_longitude_ref == 'W':
                lon_decimal = -lon_decimal
                
            return {
                "latitude": lat_decimal,
                "longitude": lon_decimal,
                "altitude": getattr(exif_image, 'gps_altitude', None)
            }
    except Exception as e:
        print(f"Error extracting EXIF data: {str(e)}")
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
        with open(f"static/attachments/{attachment_id}.{attachment_name.split('.')[-1]}", "wb") as f:
            f.write(attachment_content)

    # Return email ID
    return email_id
