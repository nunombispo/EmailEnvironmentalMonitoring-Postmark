import base64
from fastapi import FastAPI, Request
import json
from PIL import Image
from exif import Image as ExifImage
import io
from typing import Optional, Dict, Any



def get_geo_info(image_data: bytes) -> Optional[Dict[str, Any]]:
    """
    Extracts GPS information from an image.
    
    Args:
        image_data: bytes - The image data to extract GPS information from.
        
    Returns:	
        dict - A dictionary containing the GPS information if found, otherwise None.
    """

    try:
        # Create an in-memory file-like object
        image_stream = io.BytesIO(image_data)
        
        # Try to get EXIF data
        exif_image = ExifImage(image_stream)
        
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


# Initialize the FastAPI app
app = FastAPI(title="Postmark Webhook Receiver")


# Define the route for the webhook
@app.post("/webhook")
async def postmark_webhook(request: Request):
    """
    Handles the Postmark webhook.
    
    Args:
        request: Request - The incoming request object.
        
    Returns:
        dict - A dictionary containing the status and message.
    """
    
    # Get the raw JSON data from the request
    data = await request.json()
    
    # Get the From information
    from_email = data.get("FromFull").get("Email")
    from_name = data.get("FromFull").get("Name")
    
    # Get the To information
    to_email = data.get("ToFull")[0].get("Email")
    to_name = data.get("ToFull")[0].get("Name")
    to_mailbox_hash = data.get("ToFull")[0].get("MailboxHash")
    
    # Get the date and time of the email
    date_time = data.get("Date")
    
    # Get the subject of the email
    subject = data.get("Subject")
    
    # Get the text body of the email
    text_body = data.get("TextBody")
    
    # Get the HTML body of the email
    html_body = data.get("HtmlBody")
    
    # Get the attachments
    attachments = data.get("Attachments", [])
    attachment_list = []
    for attachment in attachments:
        # Get the attachment info
        attachment_name = attachment.get("Name")
        attachment_content_type = attachment.get("ContentType")
        attachment_content_length = attachment.get("ContentLength")
        attachment_content = attachment.get("Content")
        
        # Decode base64 content
        decoded_content = base64.b64decode(attachment_content)
        
        # Check if it's an image and extract geo info
        geo_info = None
        if attachment_content_type.startswith('image/'):
            geo_info = get_geo_info(decoded_content)
        
        # Create the attachment info
        attachment_info = {
            "name": attachment_name,
            "content_type": attachment_content_type,
            "content_length": attachment_content_length,
            "decoded_content": decoded_content,
            "geo_info": geo_info
        }
        
        # Append the attachment info to the list
        attachment_list.append(attachment_info)
    
    # Return the status and message
    return {"status": "success", "message": "Webhook received successfully"}