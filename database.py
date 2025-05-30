import sqlite3
from datetime import datetime, UTC
import hashlib
import time

def get_db_connection():
    conn = sqlite3.connect('email_monitoring.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create emails table
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_email TEXT,
            from_name TEXT,
            to_email TEXT,
            to_name TEXT,
            to_mailbox_hash TEXT,
            subject TEXT,
            text_body TEXT,
            html_body TEXT,
            date_received TIMESTAMP,
            submission_hash TEXT UNIQUE
        )
    ''')
    
    # Create attachments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER,
            name TEXT,
            content_type TEXT,
            content_length INTEGER,
            content BLOB,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            FOREIGN KEY (email_id) REFERENCES emails (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_email(email_data):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Generate a unique hash for the submission
    submission_hash = hashlib.sha256(
        f"{email_data.get('from_email')}{email_data.get('subject')}{time.time()}".encode()
    ).hexdigest()[:12]  # Using first 12 characters for readability
    
    # Insert email data
    c.execute('''
        INSERT INTO emails (
            from_email, from_name, to_email, to_name, to_mailbox_hash,
            subject, text_body, html_body, date_received, submission_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email_data.get('from_email'),
        email_data.get('from_name'),
        email_data.get('to_email'),
        email_data.get('to_name'),
        email_data.get('to_mailbox_hash'),
        email_data.get('subject'),
        email_data.get('text_body'),
        email_data.get('html_body'),
        datetime.now(UTC),
        submission_hash
    ))
    
    email_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return email_id, submission_hash

def save_attachment(attachment_data):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Insert attachment data
    c.execute('''
        INSERT INTO attachments (
            email_id, name, content_type, content_length,
            content, latitude, longitude, altitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        attachment_data.get('email_id'),
        attachment_data.get('name'),
        attachment_data.get('content_type'),
        attachment_data.get('content_length'),
        attachment_data.get('content'),
        attachment_data.get('latitude'),
        attachment_data.get('longitude'),
        attachment_data.get('altitude')
    ))
    
    attachment_id = c.lastrowid

    conn.commit()
    conn.close()
    return attachment_id
