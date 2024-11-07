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

    # Calculate the content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Determine the relative path without MODSECURITY_RULES_DIR
    relative_path = os.path.relpath(
        MODSECURITY_CONF_PATH if config_type == 'modsecurity' else CRS_CONF_PATH, 
        'path-to-repo'
    )

    # Query the database for the configuration entry
    config = session.query(ModsecRule).filter_by(rule_code=config_codes[config_type]).first()
    
    if not config:
        # Create a new config entry if it doesn't exist
        config = ModsecRule(
            rule_code=config_codes[config_type],
            rule_name=f"{config_type.title()} Configuration",
            rule_path=relative_path,  # Store the relative path for the config file
            content_hash=current_hash,
            is_modified=True,
            last_modified=datetime.now()
        )
        session.add(config)
    else:
        # Update existing config entry if the content hash has changed
        if config.content_hash != current_hash:
            config.content_hash = current_hash
            config.is_modified = True
            config.last_modified = datetime.now()
        else:
            # Reset is_modified to False if the content is unchanged
            config.is_modified = False

    session.commit()
    return True
