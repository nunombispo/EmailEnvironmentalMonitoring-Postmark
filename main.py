import base64
from fastapi import FastAPI, Request
import uvicorn
import database
from contextlib import asynccontextmanager
from utils import get_geo_info, save_email_and_attachments


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database.init_db()
    yield
    # Shutdown
    pass


# Initialize the FastAPI app
app = FastAPI(title="Postmark Webhook Receiver", lifespan=lifespan)


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
    
    # Prepare email data
    email_data = {
        'from_email': data.get("FromFull", {}).get("Email"),
        'from_name': data.get("FromFull", {}).get("Name"),
        'to_email': data.get("ToFull", [{}])[0].get("Email"),
        'to_name': data.get("ToFull", [{}])[0].get("Name"),
        'to_mailbox_hash': data.get("ToFull", [{}])[0].get("MailboxHash"),
        'subject': data.get("Subject"),
        'text_body': data.get("TextBody"),
        'html_body': data.get("HtmlBody")
    }
    
    # Process attachments
    attachments = data.get("Attachments", [])
    attachments_data = []
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
        
        # Prepare attachment data
        attachment_data = {
            'name': attachment_name,
            'content_type': attachment_content_type,
            'content_length': attachment_content_length,
            'content': decoded_content,
            'latitude': geo_info.get("latitude") if geo_info else None,
            'longitude': geo_info.get("longitude") if geo_info else None,
            'altitude': geo_info.get("altitude") if geo_info else None
        }

        # Add email_id to attachment
        attachments_data.append(attachment_data)

    # Save email and attachments
    save_email_and_attachments(email_data, attachments_data)
    
    # Return the status and message
    return {"status": "success", "message": "Webhook received successfully"}


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)