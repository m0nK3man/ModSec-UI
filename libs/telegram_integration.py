import requests

def send_test_message(bot_token, chat_id, message="This is a test message from ModSecurity UI."):
    """
    Sends a test message to a Telegram chat.

    :param bot_token: Telegram Bot API token (string)
    :param chat_id: Telegram chat ID (string or int)
    :param message: Message text to send (string, optional)
    :return: Response from Telegram API or an error message
    """
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(telegram_api_url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return {"success": True, "response": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}
