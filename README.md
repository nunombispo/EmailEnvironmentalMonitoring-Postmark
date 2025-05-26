# Email Environmental Monitoring System

A FastAPI application that receives and processes environmental monitoring data via email, powered by Postmark's inbound email parsing. The system automatically processes submissions, extracts geolocation data from images, and sends confirmation emails to submitters.

## 🌟 Features

- **Email-based Data Collection**: Submit environmental data by simply sending an email
- **Automatic Image Processing**: Extracts GPS coordinates and altitude from image metadata
- **Priority-based Processing**: Support for different priority levels (high, medium, low)
- **Web Interface**: View all submissions with a modern, responsive UI
- **Search & Filter**: Easily find submissions by subject, sender, or ID
- **Automated Confirmations**: Automatic email confirmations for each submission
- **Attachment Support**: Handles multiple image attachments with geolocation data

## 🚀 Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd EmailEnvironmentalMonitoring-Postmark
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Required for sending confirmation emails
export POSTMARK_API_TOKEN='your-postmark-api-token'
```

5. Create required directories:

```bash
mkdir -p static/attachments
```

## 🏃‍♂️ Running the Application

Start the server with:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## 📧 Making Submissions

Send an email to your configured Postmark inbound address with:

- Subject: Your observation title
- Body: Your environmental monitoring data
- Attachments: Images with geolocation data (optional)

The system will:

1. Process your submission
2. Extract any geolocation data from images
3. Store the data in the database
4. Send you a confirmation email with your submission ID

## 🔍 Viewing Submissions

Access the web interface at `http://localhost:8000` to:

- View all submissions in a card-based layout
- See images with their geolocation data
- Search submissions by subject, sender, or ID
- Filter by priority level

## 🛠️ API Documentation

Once the server is running, access the automatic API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 Database Schema

The application uses SQLite with two main tables:

### Emails Table

- `id`: Primary key
- `from_email`: Sender's email
- `from_name`: Sender's name
- `to_email`: Recipient email
- `to_name`: Recipient name
- `to_mailbox_hash`: Priority level
- `subject`: Email subject
- `text_body`: Plain text content
- `html_body`: HTML content
- `date_received`: Timestamp
- `submission_hash`: Unique identifier

### Attachments Table

- `id`: Primary key
- `email_id`: Foreign key to emails
- `name`: Original filename
- `content_type`: MIME type
- `content_length`: File size
- `content`: Binary data
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `altitude`: GPS altitude

## 🔒 Security Considerations

- All file uploads are validated and sanitized
- Images are stored with unique identifiers
- Email confirmations are sent via Postmark's secure API
- Database connections are properly managed and closed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
