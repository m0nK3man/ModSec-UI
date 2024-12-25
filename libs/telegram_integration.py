import requests
from datetime import datetime, timedelta
from libs.elasticsearch_client import ElasticsearchClient
import json

es_client = ElasticsearchClient()

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

def send_alert(bot_token, chat_id):
    try:
        # Get the host messages data from the last 24 hours
        end_time = datetime.utcnow()  # Current time in UTC
        start_time = end_time - timedelta(hours=24)  # 24 hours ago
        result = es_client.get_host_msg(start_time=start_time, end_time=end_time)
        
        # Prepare message
        message = f"{end_time.strftime('%d/%m/%Y')} example-waf-hostname\n\n"
        
        # Iterate through the result to construct the message
        for host, alerts in result['msg_breakdown'].items():
            # Check if host has alerts
            if alerts:
                message += f"Host: {host}\n"
                for alert, count in alerts.items():
                    if alert:  # Skip empty alerts
                        message += f"  - {alert}: {count} occurrences\n"
                message += "\n"
        
        # Sending message via Telegram Bot API
        response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={'chat_id': chat_id, 'text': message}
        )
        
        # Check if the message was sent successfully
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Response: {response.text}")

    except Exception as e:
        print(f"Error occurred: {e}")
