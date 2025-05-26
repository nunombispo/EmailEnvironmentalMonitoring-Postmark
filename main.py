import base64
from fastapi import FastAPI, Request
import uvicorn
import database
from contextlib import asynccontextmanager
from utils import get_geo_info, save_email_and_attachments
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database.init_db()
    yield
    # Shutdown
    pass


# Initialize the FastAPI app
app = FastAPI(title="Postmark Webhook Receiver", lifespan=lifespan)

# Mount templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


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
        'to_mailbox_hash': data.get("ToFull", [{}])[0].get("MailboxHash", "low"),
        'subject': data.get("Subject"),
        'text_body': data.get("TextBody"),
        'html_body': data.get("HtmlBody")
    }

    # If the to_mailbox_hash is empty, set it to "low"
    if email_data.get("to_mailbox_hash") == "":
        email_data["to_mailbox_hash"] = "low"
    
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


@app.get("/", response_class=HTMLResponse)
async def display_emails(request: Request):
    """
    Display all emails and their attachments in a web interface.
    """
    conn = database.get_db_connection()
    emails = conn.execute('''
        SELECT 
            e.*,
            GROUP_CONCAT(a.id) as attachment_ids,
            GROUP_CONCAT(a.name) as attachment_names,
            GROUP_CONCAT(COALESCE(a.latitude, '')) as latitudes,
            GROUP_CONCAT(COALESCE(a.longitude, '')) as longitudes,
            GROUP_CONCAT(COALESCE(a.altitude, '')) as altitudes
        FROM emails e
        LEFT JOIN attachments a ON e.id = a.email_id
        GROUP BY e.id
        ORDER BY e.date_received DESC
    ''').fetchall()
    
    # Process the concatenated values into lists
    processed_emails = []
    for email in emails:
        email_dict = dict(email)
        if email_dict['attachment_ids']:
            # Split the concatenated values, handling NULL values
            ids = email_dict['attachment_ids'].split(',')
            names = email_dict['attachment_names'].split(',')
            lats = email_dict['latitudes'].split(',') if email_dict['latitudes'] else []
            lons = email_dict['longitudes'].split(',') if email_dict['longitudes'] else []
            alts = email_dict['altitudes'].split(',') if email_dict['altitudes'] else []
            
            email_dict['attachments'] = []
            for i in range(len(ids)):
                attachment = {
                    'id': ids[i],
                    'name': names[i],
                    'latitude': None,
                    'longitude': None,
                    'altitude': None,
                    'file_name': ids[i]
                }

                # Only add geo data if it exists and is not empty
                if i < len(lats) and lats[i] and lats[i] != '':
                    try:
                        attachment['latitude'] = float(lats[i])
                    except (ValueError, TypeError):
                        pass
                        
                if i < len(lons) and lons[i] and lons[i] != '':
                    try:
                        attachment['longitude'] = float(lons[i])
                    except (ValueError, TypeError):
                        pass
                        
                if i < len(alts) and alts[i] and alts[i] != '':
                    try:
                        attachment['altitude'] = float(alts[i])
                    except (ValueError, TypeError):
                        pass
                
                email_dict['attachments'].append(attachment)
        else:
            email_dict['attachments'] = []
        
        # Remove the concatenated fields
        for field in ['attachment_ids', 'attachment_names', 'latitudes', 'longitudes', 'altitudes']:
            del email_dict[field]
            
        processed_emails.append(email_dict)
    
    conn.close()
    
    return templates.TemplateResponse(
        "emails.html",
        {"request": request, "emails": processed_emails}
    )


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)