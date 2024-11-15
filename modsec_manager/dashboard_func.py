from datetime import datetime
from libs.var import MODSECURITY_CONF_PATH
from libs.database import Session
from libs.utils import track_config_content

def get_current_mode():
    try:
        with open(MODSECURITY_CONF_PATH, 'r') as f:
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
        with open(MODSECURITY_CONF_PATH, 'r') as f:
            lines = f.readlines()

        # Update the SecRuleEngine line with the new mode
        for i in range(len(lines)):
            if "SecRuleEngine" in lines[i]:
                lines[i] = f"SecRuleEngine {mode}\n"  # Update the line with the new mode
                break  # Exit after updating the mode

        # Write the updated configuration back to the file
        with open(MODSECURITY_CONF_PATH, 'w') as f:
            f.writelines(lines)

        # Track the configuration change in the database
        session = Session()
        content = ''.join(lines)  # Join the lines back into a single string for tracking
        track_config_content(session, 'modsecurity', content)  # Track the updated content
        session.commit()  # Commit the session to save changes to the database
        session.close()
        
        return True
    except Exception as e:
        print(f"Error updating mode: {e}")
        if session:
            session.rollback()  # Rollback the session in case of error
        return False
