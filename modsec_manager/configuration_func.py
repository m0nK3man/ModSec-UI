import os
from libs.database import Session, track_config_change
from libs.var import MODSECURITY_CONF_PATH, CRS_CONF_PATH
from models import ModsecRule

def read_modsecurity_conf():
    """Read ModSecurity configuration and check for changes"""
    session = Session()
    try:
        with open(MODSECURITY_CONF_PATH, 'r') as f:
            content = f.read()

        # Check for changes
        config = session.query(ModsecRule).filter_by(rule_code='CONFIG_MODSEC').first()

        return {
            'content': content,
            'changed': config.is_modified if config else False
        }
    finally:
        session.close()

def read_crs_conf():
    """Read CRS configuration and check for changes"""
    session = Session()
    try:
        with open(CRS_CONF_PATH, 'r') as f:
            content = f.read()

        # Check for changes
        config = session.query(ModsecRule).filter_by(rule_code='CONFIG_CRS').first()

        return {
            'content': content,
            'changed': config.is_modified if config else False
        }
    finally:
        session.close()

def save_modsecurity_conf(content):
    """Save ModSecurity configuration and track changes"""
    session = Session()
    try:
        with open(MODSECURITY_CONF_PATH, 'w') as f:
            f.write(content)

        track_config_change(session, 'modsecurity', content)
        return True
    except Exception as e:
        print(f"Error saving modsecurity.conf: {e}")
        return False
    finally:
        session.close()

def save_crs_conf(content):
    """Save CRS configuration and track changes"""
    session = Session()
    try:
        with open(CRS_CONF_PATH, 'w') as f:
            f.write(content)

        track_config_change(session, 'crs', content)
        return True
    except Exception as e:
        print(f"Error saving crs-setup.conf: {e}")
        return False
    finally:
        session.close()
