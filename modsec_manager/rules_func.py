import os
from libs.database import Session
from libs.utils import track_rule_change
from models import ModsecRule
from libs.var import MODSECURITY_RULES_DIR

def list_rules():
    """List all rules with their change status from the database"""
    session = Session()
    all_rules = []

    try:
        # Exclude config entries
        rules = session.query(ModsecRule).filter(
            ~ModsecRule.rule_code.in_(['CONFIG_MODSEC', 'CONFIG_CRS'])
        ).all()

        for rule in rules:
            rule_path = os.path.join(MODSECURITY_RULES_DIR, rule.rule_path)
            if os.path.exists(rule_path):
                with open(rule_path, "r") as f:
                    content = f.read()

                rule_info = {
                    'id': rule.id,
                    'rule_code': rule.rule_code,
                    'rule_name': rule.rule_name,
                    'filename': rule.rule_path,
                    'last_modified': rule.last_modified,  # Ensure this is passed
                    'content': content,
                    'enabled': not rule.rule_path.endswith(".disable"),
                    'changed': rule.is_modified
                }
                all_rules.append(rule_info)

    finally:
        session.close()

    return all_rules

def save_rule(filename, content):
    """Save rule content and track changes in database"""
    session = Session()
    try:
        # Save file content
        with open(os.path.join(MODSECURITY_RULES_DIR, filename), "w") as f:
            f.write(content)

        # Track change in database
        track_rule_change(session, filename, content)

    finally:
        session.close()

def toggle_rule(filename, enable):
    """Enable or disable a rule and update rule path in the database."""
    session = Session()
    try:
        # Retrieve the rule from the database
        rule = session.query(ModsecRule).filter_by(rule_path=filename).first()

        if rule is None:
            raise ValueError(f"No rule found with the filename {filename}")

        # Determine the file path
        file_path = os.path.join(MODSECURITY_RULES_DIR, filename)

        # Enable or disable the rule based on the `enable` flag
        if enable:
            # Enable the rule
            if filename.endswith(".disable"):
                new_filename = filename[:-8]  # Remove the '.disable' suffix
                os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, new_filename))
                rule.rule_path = new_filename  # Update rule path in database
                rule.is_enabled = True  # Update is_enabled status
        else:
            # Disable the rule
            if not filename.endswith(".disable"):
                new_filename = f"{filename}.disable"
                os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, new_filename))
                rule.rule_path = new_filename  # Update rule path in database
                rule.is_enabled = False  # Update is_enabled status

        # Commit the changes to the database
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error toggling rule: {e}")
    finally:
        session.close()
