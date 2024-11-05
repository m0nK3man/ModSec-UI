# modsec_manager.py
import os
import subprocess
import requests
from var import MODSECURITY_RULES_DIR, MODSECURITY_CONF_PATH, CRS_CONF_PATH, GITHUB_API_URL

# ==================== Global ====================


# ==================== Home ====================

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
#        reload_nginx()
        return True
    except Exception as e:
        print(f"Error updating mode: {e}")
        return False

# ==================== Rules ====================

def list_rules():
    enabled_rules = []
    disabled_rules = []

    # List and categorize rules based on their filename (dot prefix for disabled)
    for filename in sorted(os.listdir(MODSECURITY_RULES_DIR)):
        if filename.endswith(".conf"):
            with open(os.path.join(MODSECURITY_RULES_DIR, filename), "r") as f:
                rule = {
                    'filename': filename,
                    'content': f.read(),
                    'enabled': not filename.startswith(".")
                }
                if rule['enabled']:
                    enabled_rules.append(rule)
                else:
                    disabled_rules.append(rule)

    # Return two separate lists for enabled and disabled rules
    return enabled_rules, disabled_rules

def toggle_rule(filename, enable):
    file_path = os.path.join(MODSECURITY_RULES_DIR, filename)
    if enable:
        # Remove dot prefix to enable
        if filename.startswith("."):
            os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, filename[1:]))
    else:
        # Add dot prefix to disable
        if not filename.startswith("."):
            os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, f".{filename}"))
#    reload_nginx()

def save_rule(filename, content):
    with open(os.path.join(MODSECURITY_RULES_DIR, filename), "w") as f:
        f.write(content)
#    reload_nginx()

# ==================== Configuration ====================

def read_modsecurity_conf():
    with open(MODSECURITY_CONF_PATH, 'r') as f:
        return f.read()

def save_modsecurity_conf(content):
    try:
        with open(MODSECURITY_CONF_PATH, 'w') as f:
            f.write(content)
#        reload_nginx()
        return True
    except Exception as e:
        print(f"Error saving modsecurity.conf: {e}")
        return False

def read_crs_conf():
    with open(CRS_CONF_PATH, 'r') as f:
        return f.read()

def save_crs_conf(content):
    try:
        with open(CRS_CONF_PATH, 'w') as f:
            f.write(content)
#        reload_nginx()
        return True
    except Exception as e:
        print(f"Error saving crs-setup.conf: {e}")
        return False

