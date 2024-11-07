from datetime import datetime
from libs.var import MODSECURITY_CONF_PATH

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
    try:
        with open(MODSECURITY_CONF_PATH, 'r') as f:
            lines = f.readlines()

        with open(MODSECURITY_CONF_PATH, 'w') as f:
            for line in lines:
                if "SecRuleEngine" in line:
                    f.write(f"SecRuleEngine {mode}\n")
                else:
                    f.write(line)
        return True
    except Exception as e:
        print(f"Error updating mode: {e}")
        return False
