from flask import Flask, request, jsonify
import os
import requests
import logging
from src.chat.chatbot_core import ChatbotCore
from dotenv import load_dotenv
import sys
from src.llm.llm_client import LLMClient
import traceback

# ---------- CONFIGURATION ----------

# Load environment variables
load_dotenv("keys.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WhatsApp Business API configuration
WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
WHATSAPP_VERIFY_TOKEN = os.environ["WHATSAPP_VERIFY_TOKEN"]
WHATSAPP_PHONE_NUMBER_ID = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
WHATSAPP_API_VERSION = os.environ["WHATSAPP_API_VERSION"]

# LLM API Configuration
LLM_AZURE_ENDPOINT = os.environ["LLM_AZURE_ENDPOINT"]
LLM_AZURE_OPENAI_KEY = os.environ["LLM_AZURE_OPENAI_KEY"]
LLM_AZURE_MODEL_NAME = os.environ["LLM_AZURE_MODEL_NAME"]
STT_AZURE_MODEL_NAME = os.environ["STT_AZURE_MODEL_NAME"]
# Initialize Flask app
app = Flask(__name__)

# Initialize the chatbot core - each session will have its own instance
active_sessions = {}

# Initialize STT client globally
stt_client = LLMClient(
    azure_endpoint=LLM_AZURE_ENDPOINT,
    azure_openai_key=LLM_AZURE_OPENAI_KEY,
    model_name=STT_AZURE_MODEL_NAME
)

# ---------- HELPER FUNCTIONS ----------

def get_or_create_session(phone_number):
    """
    Get an existing session or create a new one for a phone number
    
    Args:
        phone_number (str): User's WhatsApp phone number
        
    Returns:
        ChatbotCore: Instance of the chatbot for this user
    """
    if phone_number not in active_sessions:
        logger.info(f"Creating new session for {phone_number}")
        active_sessions[phone_number] = ChatbotCore(azure_endpoint=LLM_AZURE_ENDPOINT, azure_openai_key=LLM_AZURE_OPENAI_KEY, azure_model_name=LLM_AZURE_MODEL_NAME)
    return active_sessions[phone_number]

def send_whatsapp_message(phone_number, message):
    """
    Send a message to WhatsApp using the WhatsApp Business API
    
    Args:
        phone_number (str): Recipient's phone number
        message (str): Message content to send
        
    Returns:
        dict: API response
    """
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Message sent to {phone_number}: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {"error": str(e)}

def send_whatsapp_image(phone_number, image_path):
    """
    Send an image message to WhatsApp using the WhatsApp Business API
    
    Args:
        phone_number (str): Recipient's phone number
        image_path (str): Path to the image file
        
    Returns:
        dict: API response
    """
    if not image_path:
        logger.error("Image path must be provided")
        return {"error": "Image path must be provided"}
    
    try:
        # First upload the image to get an ID
        upload_url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/media"
        
        upload_headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        # Open the image file for upload
        with open(image_path, 'rb') as image_file:
            upload_data = {
                'messaging_product': (None, 'whatsapp'),
                'file': (os.path.basename(image_path), image_file, 'image/jpeg')
            }
            # Upload the image
            upload_response = requests.post(
                upload_url,
                headers=upload_headers,
                files=upload_data
            )
            print(upload_response.text)
        upload_response.raise_for_status()
        image_id = upload_response.json().get('id')
        
        if not image_id:
            logger.error(f"Failed to get image_id: {upload_response.text}")
            return {"error": "Failed to upload image"}
        
        # Now send the message with the image ID
        url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "image",
            "image": {
                "id": image_id
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Image sent to {phone_number}: {response.status_code}")
        
        # Delete the image file after sending
        try:
            os.remove(image_path)
            logger.info(f"Successfully deleted image file: {image_path}")
        except Exception as e:
            logger.error(f"Error deleting image file {image_path}: {str(e)}")
        
        return response.json()
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp image: {str(e)}")
        return {"error": str(e)}

def mark_message_as_read(message_id):
    """
    Mark a WhatsApp message as read (blue tick)
    
    Args:
        message_id (str): The ID of the message to mark as read
        
    Returns:
        dict: API response
    """
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Message marked as read: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"Error marking message as read: {str(e)}")
        return {"error": str(e)}

def download_media(media_id):
    """
    Download media from WhatsApp Business API and return as binary data
    
    Args:
        media_id (str): The ID of the media to download
        
    Returns:
        bytes or None: The media content or None if download failed
    """
    try:
        # First, get the media URL
        url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{media_id}"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        # Get the media URL
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get media URL: {response.status_code} {response.text}")
            return None
        
        media_info = response.json()
        
        # Download the media
        media_url = media_info.get('url')
        if not media_url:
            logger.error("No media URL found in response")
            return None
        
        media_response = requests.get(media_url, headers=headers)
        if media_response.status_code != 200:
            logger.error(f"Failed to download media: {media_response.status_code}")
            return None
        
        # Return the media content directly
        return media_response.content
    
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        return None

# ---------- MESSAGE PROCESSING FUNCTIONS ----------

def process_text_message(phone_number, message_text):
    """
    Process a text message from WhatsApp
    
    Args:
        phone_number (str): Sender's phone number
        message_text (str): The text message content
        
    Returns:
        bool: Success status
    """
    try:
        logger.info(f"Processing text message from {phone_number}: {message_text}")
        
        # Get or create a session for this user
        chatbot = get_or_create_session(phone_number)
        
        # Process the message
        result = chatbot.process_message(message_text)
        
        # Send each response to WhatsApp
        for response in result["responses"]:
            send_whatsapp_message(phone_number, response)
            
        if result.get("image_path"):
            send_whatsapp_image(phone_number, result["image_path"])
        
        return True
    except Exception as e:
        logger.error(f"Error processing text message: {str(e)}")
        return False

def process_voice_message(phone_number, media_id):
    """
    Process a voice message from WhatsApp
    
    Args:
        phone_number (str): Sender's phone number
        media_id (str): The ID of the voice message media
        
    Returns:
        bool: Success status
    """
    try:
        logger.info(f"Processing voice message from {phone_number}")
        
        if not media_id:
            send_whatsapp_message(
                phone_number, 
                "Sorry, I couldn't process your voice message."
            )
            return False
        
        # Download the voice note content
        voice_data = download_media(media_id)
        
        if not voice_data:
            send_whatsapp_message(
                phone_number, 
                "Sorry, I couldn't process your voice message."
            )
            return False
        
        # Transcribe the audio using global STT client
        text = stt_client.call_stt(voice_data, media_id)
        
        if not text:
            send_whatsapp_message(
                phone_number, 
                "Sorry, I couldn't understand the audio in your voice message."
            )
            return False
        
        logger.info(f"Transcribed voice message: {text}")
        
        # Process like a regular text message
        chatbot = get_or_create_session(phone_number)
        result = chatbot.process_message(text)
        
        # Send each response to WhatsApp
        print(result)
        for response in result["responses"]:
            send_whatsapp_message(phone_number, response)
            
        if result.get("image_path"):
            send_whatsapp_image(phone_number, result["image_path"])
        
        return True
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        send_whatsapp_message(
            phone_number, 
            "Sorry, I encountered an error processing your voice message."
        )
        return False

# ---------- FLASK ROUTES ----------

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Handle the initial webhook verification by WhatsApp
    """
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            # Respond with the challenge token from the request
            logger.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Respond with 403 if verify tokens do not match
            logger.warning("Verification failed: token mismatch")
            return "Verification failed", 403
    
    return "Bad Request", 400

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming messages from WhatsApp
    """
    # Get the request body
    data = request.json
    logger.info(f"Received webhook data: {data}")
    
    # Check if this is a WhatsApp message
    if data.get('object') == 'whatsapp_business_account':
        try:
            # Process each entry in the webhook
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # Process each message
                    for message in value.get('messages', []):
                        # Get the sender's phone number and message ID
                        phone_number = message.get('from')
                        message_id = message.get('id')
                        
                        # Mark the message as read (blue tick)
                        mark_message_as_read(message_id)   
                        
                        # Process by message type
                        if message.get('type') == 'text':
                            message_text = message.get('text', {}).get('body', '')
                            process_text_message(phone_number, message_text)
                            
                        elif message.get('type') == 'audio' or message.get('type') == 'voice':
                            media_id = message.get('audio', {}).get('id') or message.get('voice', {}).get('id')
                            process_voice_message(phone_number, media_id)
                            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            logger.error(traceback.format_exc())
    
    # Always return a 200 OK to acknowledge receipt of the webhook
    return "OK", 200

@app.route('/status', methods=['GET'])
def status():
    """
    Check the status of the webhook server
    """
    return jsonify({
        "status": "running",
        "active_sessions": len(active_sessions)
    })

# ---------- MAIN ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting WhatsApp webhook server on port {port}")
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=True,
    ) 