import requests
from datetime import datetime

def send_test_message(bot_token, chat_id):
    # Get the current time in a readable format
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create an HTML-formatted message with color and the current time
    message_text = f"""
    <b>This is a test message from the ModSec UI.</b>\n
    <i>Sent at: {current_time}</i>\n
    <u>Styled message without unsupported tags!</u>
    """
    
    # URL to send the message to Telegram API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",  # Ensure Telegram interprets the HTML
    }

    try:
        # Sending the request to the Telegram Bot API
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return {"success": True}
    except requests.exceptions.HTTPError as e:
        error_response = response.json()  # Parse JSON error response from Telegram
        return {
            "success": False,
            "error": error_response.get("description", "An unknown error occurred")
        }
    except Exception as e:
        # Catch any other errors
        return {
            "success": False,
            "error": str(e)
        }
