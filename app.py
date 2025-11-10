import os
from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import json

app = Flask(__name__, static_folder='static')

# Environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From', '')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    if 'hello' in incoming_msg or 'hi' in incoming_msg:
        msg.body('Welcome to Immigration Services! How can I help you today?')
    elif 'status' in incoming_msg:
        msg.body('Your application status: Under Review')
    else:
        msg.body('Thank you for your message. Our team will respond shortly.')
    
    return str(resp)

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
