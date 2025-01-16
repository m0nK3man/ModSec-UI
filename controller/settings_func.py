import os
import json

# Default Configuration
DEFAULT_CONFIG = {
    "LOCAL_CONF_PATH": "local-conf/",
    "MODSECURITY_CONF_PATH": "local-conf/modsecurity.conf",
    "CRS_CONF_PATH": "local-conf/crs/crs-setup.conf",
    "MODSECURITY_RULES_DIR": "local-conf/crs/rules",
    "GIT_REPO_PATH": "/root/modsec-ui",
    "GIT_AUTHOR_NAME": "ModSecurity UI",
    "GIT_AUTHOR_EMAIL": "modsec-ui@bravo.com",
    "ELASTICSEARCH_CONFIG": {
        "HOST": "https://172.16.20.31:9200",
        "USER": "elastic",
        "PASSWORD": "BravoSOC@2024",
        "INDEX_MODSEC": "modsec-*",
        "INDEX_ACCESS": "nginx-access-logs-*",
        "INDEX_ERROR": "nginx-error-logs-*",
        "MAX_RESULTS": 100
    "Instances": {}
    },
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
    "TELEGRAM_ALERT": False,
}

# Config file path
CONFIG_FILE = os.path.join(os.getcwd(), "config.json")

# Load or initialize configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
#        print(f"Loading configuration from file: {CONFIG_FILE}")
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        print(f"Configuration file not found at {CONFIG_FILE}, using default settings.")
        return DEFAULT_CONFIG

def save_config(config):
    try:  # The `try` block starts here
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
        return True  # Return True if successful
    except Exception as e:  # `except` must align with `try`
        print(f"Error saving config: {e}")  # Log the error for debugging
        return False  # Return False if there's an exception
