import requests

def send_test_message(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": "This is a test message from the ModSec UI.",
    }
    try:
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
