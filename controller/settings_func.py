import os
import json
import shutil

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
    },
    "Instances": {},
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


BASE_TEMPLATE_DIR = os.path.join(os.getcwd(), "instances", "based-template")

def sync_local_conf_dirs(instances):
    """
    Sync the directories in `instances` with the `Instances` in config.json.
    Adds new instance directories and removes those that no longer exist in the config.
    """
    local_conf_dir = os.path.join(os.getcwd(), "instances")
    
    # Sanitize instance names for folder names
    instance_dirs = {name.replace(" ", "-") for name in instances.keys()}

    # List existing instance directories
    existing_dirs = {d for d in os.listdir(local_conf_dir) if os.path.isdir(os.path.join(local_conf_dir, d))}

    # Add new directories
    for instance in instance_dirs - existing_dirs:
        instance_path = os.path.join(local_conf_dir, instance)
        try:
            shutil.copytree(BASE_TEMPLATE_DIR, instance_path)
            print(f"Created folder: {instance_path}")
        except Exception as e:
            print(f"Error creating folder {instance_path}: {e}")

    # Remove directories that no longer exist in the config
    for instance in existing_dirs - instance_dirs:
        if instance != "based-template":  # Don't delete the base template
            instance_path = os.path.join(local_conf_dir, instance)
            try:
                shutil.rmtree(instance_path)
                print(f"Deleted folder: {instance_path}")
            except Exception as e:
                print(f"Error deleting folder {instance_path}: {e}")
