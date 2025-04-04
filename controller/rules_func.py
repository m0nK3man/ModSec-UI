import os
from libs.database import db
from libs.utils import track_rule_content, update_is_modified
from models import ModsecRule
from controller.settings_func import load_config
config = load_config()

def list_rules():
    """List all rules with their change status from the database"""
    all_rules = []

    try:
        # Exclude config entries
        rules = db.session.query(ModsecRule).filter(
            ~ModsecRule.rule_code.in_(['CONFIG_MODSEC', 'CONFIG_CRS'])
        ).all()

        for rule in rules:
            rule_path = os.path.join(config['MODSECURITY_RULES_DIR'], rule.rule_path)
            if os.path.exists(rule_path):
                with open(rule_path, "r") as f:
                    content = f.read()
                
                rule_info = {
                    'id': rule.id,
                    'rule_code': rule.rule_code,
                    'rule_name': rule.rule_name,
                    'filename': rule.rule_path,
                    'last_modified': rule.last_modified,  # Ensure this is passed
                    'content': content,  # Use to calculate hash
                    'content_change': rule.is_content_change,  # Check content modified by hash
                    'enabled': rule.is_enabled,  # Current status
                    'modified': rule.is_modified  # is_modified = is_content_change + rule.is_enabled mismatch
                }
                all_rules.append(rule_info)

    except Exception as e:
        print(f"Error listing rules: {e}")

    return all_rules

def save_rule(filename, content):
    """Save rule content and track changes in database"""
    try:
        # Save file content
        with open(os.path.join(config['MODSECURITY_RULES_DIR'], filename), "w") as f:
            f.write(content)

        # Track change in database
        track_rule_content(db.session, filename, content)

    except Exception as e:
        print(f"Error saving rule: {e}")

def update_status(rule, enable):
    if enable:
        rule.is_enabled = True  # Update is_enabled status
    else:
        rule.is_enabled = False  # Update is_enabled status
    return True

def toggle_rule(filename, enable):
    """Enable or disable a rule and update rule path in the database."""
    try:
        # Retrieve the rule from the database
        rule = db.session.query(ModsecRule).filter_by(rule_path=filename).first()

        if rule is None:
            raise ValueError(f"No rule found with the filename {filename}")

        update_status(rule, enable)
        update_is_modified(db.session, rule)
        # Commit the changes to the database
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Error toggling rule: {e}")
