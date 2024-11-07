from models import ModsecRule
import hashlib
from datetime import datetime
from libs.var import *
import os

def track_rule_change(session, rule_path, content):
    """Track changes to rule files in the database"""
    rule = session.query(ModsecRule).filter_by(rule_path=rule_path).first()
    if not rule:
        # Logic to handle case where rule doesn't exist (optional)
        return False

    # Calculate current content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Only update the modified state
    if rule.content_hash != current_hash:
        rule.is_modified = True
    else:
        rule.is_modified = False  # Reset if unchanged

    session.commit()  # Commit the change to is_modified only
    return True

def track_config_change(session, config_type, content):
    """Track changes to configuration files in the database"""
    # Define config codes
    config_codes = {
        'modsecurity': 'CONFIG_MODSEC',
        'crs': 'CONFIG_CRS'
    }

    # Calculate current content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Query the database for the configuration entry
    config = session.query(ModsecRule).filter_by(rule_code=config_codes[config_type]).first()
    
    if not config:
        # Create a new config entry if it doesn't exist
        config = ModsecRule(
            rule_code=config_codes[config_type],
            rule_name=f"{config_type.title()} Configuration",
            rule_path=MODSECURITY_CONF_PATH if config_type == 'modsecurity' else CRS_CONF_PATH,
            content_hash=current_hash,
            is_modified=False,
            last_modified=datetime.now()
        )
        session.add(config)
    else:
        # Update modified state based on hash comparison
        config.is_modified = (config.content_hash != current_hash)

    session.commit()
    return True
