import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Environment variables - NO DEFAULT VALUES for security
ACCESS_TOKEN = os.getenv('WA_ACCESS_TOKEN')
WA_PHONE_ID = os.getenv('WA_PHONE_ID')
WA_VERIFY_TOKEN = os.getenv('WA_VERIFY_TOKEN')
APPSCRIPT_URL = os.getenv('APPSCRIPT_URL')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
CALENDLY_URL = os.getenv('CALENDLY_URL', '')
CAL_TZ = os.getenv('CAL_TZ', 'Europe/London')
MAX_MEDIA_BYTES = int(os.getenv('MAX_MEDIA_BYTES', 12582912))
SHEET_ID = os.getenv('SHEET_ID')
SHEET_TAB = os.getenv('SHEET_TAB', 'Cases')

@app.route('/', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook with WhatsApp"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == WA_VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        
        # Process messages
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change and 'messages' in change['value']:
                            messages = change['value']['messages']
                            for message in messages:
                                from_number = message.get('from')
                                msg_body = message.get('text', {}).get('body', '')
                                
                                # Send response
                                send_whatsapp_message(from_number, f"Received: {msg_body}")
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error'}), 500

def send_whatsapp_message(to_number, message_text):
    """Send WhatsApp message via Cloud API"""
    url = f"https://graph.facebook.com/v17.0/{WA_PHONE_ID}/messages"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'text': {'body': message_text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
