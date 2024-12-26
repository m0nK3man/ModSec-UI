from datetime import datetime
from libs.database import db  # Import db instead of Session
from libs.utils import track_config_content
from controller.settings_func import load_config
config = load_config()

def get_current_mode():
    try:
        with open(config['MODSECURITY_CONF_PATH'], 'r') as f:
            for line in f:
                if "SecRuleEngine" in line:
                    return line.split()[1]
    except FileNotFoundError:
        return "Unknown"
    return "Unknown"

def set_mode(mode):
    """Set the WAF mode in the ModSecurity configuration."""
    try:
        # Read the existing configuration
        with open(config['MODSECURITY_CONF_PATH'], 'r') as f:
            lines = f.readlines()

        # Update the SecRuleEngine line with the new mode
        for i in range(len(lines)):
            if "SecRuleEngine" in lines[i]:
                lines[i] = f"SecRuleEngine {mode}\n"  # Update the line with the new mode
                break  # Exit after updating the mode

        # Write the updated configuration back to the file
        with open(config['MODSECURITY_CONF_PATH'], 'w') as f:
            f.writelines(lines)

        # Track the configuration change in the database
        content = ''.join(lines)  # Join the lines back into a single string for tracking
        track_config_content(db.session, 'modsecurity', content)  # Track the updated content
        db.session.commit()  # Commit the session to save changes to the database

        return True
    except Exception as e:
        print(f"Error updating mode: {e}")
        db.session.rollback()  # Rollback the session in case of error
        return False
