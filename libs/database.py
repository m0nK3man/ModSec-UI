from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ModsecRule
import hashlib
from datetime import datetime

# Database connection
engine = create_engine('postgresql://modsec_admin:bravo123@localhost/modsec_ui')
Session = sessionmaker(bind=engine)

def track_rule_change(session, rule_path, content):
    """Track changes to rule files in the database"""
    rule = session.query(ModsecRule).filter_by(rule_path=rule_path).first()
    if not rule:
        return False

    # Calculate current content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Update rule change tracking
    if rule.content_hash != current_hash:
        rule.content_hash = current_hash
        rule.is_modified = True
        rule.last_modified = datetime.now()
    else:
        # Reset is_modified to False if the content is the same as original
        rule.is_modified = False

    session.commit()
    return True

def track_config_change(session, config_type, content):
    """Track changes to configuration files in the database"""
    # For config files, we'll use special reserved rule_codes
    config_codes = {
        'modsecurity': 'CONFIG_MODSEC',
        'crs': 'CONFIG_CRS'
    }

    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    config = session.query(ModsecRule).filter_by(rule_code=config_codes[config_type]).first()
    if not config:
        # Create config entry if it doesn't exist
        config = ModsecRule(
            rule_code=config_codes[config_type],
            rule_name=f"{config_type.title()} Configuration",
            rule_path=MODSECURITY_CONF_PATH if config_type == 'modsecurity' else CRS_CONF_PATH,
            content_hash=current_hash,
            is_modified=True,
            last_modified=datetime.now()
        )
        session.add(config)
    else:
        # Update existing config entry
        if config.content_hash != current_hash:
            config.content_hash = current_hash
            config.is_modified = True
            config.last_modified = datetime.now()
        else:
            # Reset is_modified to False if the content is the same as original
            config.is_modified = False

    session.commit()
    return True
