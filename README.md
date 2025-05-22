# Postmark Webhook Receiver

A simple FastAPI application that receives webhooks from Postmark.

## Setup

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the server with:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

The webhook endpoint is available at: `http://localhost:8000/webhook`

## Testing the Webhook

You can test the webhook using curl or Postman with a POST request to the webhook endpoint. Example:

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## API Documentation

Once the server is running, you can access the automatic API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
