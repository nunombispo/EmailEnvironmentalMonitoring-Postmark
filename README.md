# Email Environmental Monitoring System

A FastAPI application that receives and processes environmental monitoring data via email, powered by Postmark's inbound email parsing.

The system automatically processes submissions, extracts geolocation data from images, and sends confirmation emails to submitters.

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
git clone https://github.com/nunombispo/EmailEnvironmentalMonitoring-Postmark
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

4. Configure Postmark

- Create a Postmark account
- Create a Message Stream (type: Inbound)
- Set your Webhook URL to your server (e.g. using ngrok http 8000) at `/webook`
- Get the API key for the Transactional Message Stream (type: Outbound)

5. Set up environment variables:

Create a `.env` file with:

```bash
POSTMARK_API_TOKEN='your-postmark-api-token'
POSTMARK_SENDER_EMAIL='your-postmark-sender-email'
```

6. Create required directories:

```bash
mkdir -p static/attachments
```

## 🏃‍♂️ Running the Application

Start the server with:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

💡 You can expose your local server to the Internet and Postmark using ngrok:

`ngrok http 8000`

Prepare the ngrok URL with the endpoint of the webhook (e.g. https://xxxxxx.ngrok-free.app/webhook) and configure it as your Postmark inbound webhook URL.

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

Access the web interface at `http://localhost:8000` (or the ngrok URL) to:

- View all submissions in a card-based layout
- See images with their geolocation data
- Search submissions by subject, sender, or ID
- Filter by priority level

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
