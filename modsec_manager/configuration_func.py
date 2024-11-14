# modsec_manager/configuration_func.py
from libs.database import Session
from libs.utils import track_config_content
from libs.var import MODSECURITY_CONF_PATH, CRS_CONF_PATH
from models import ModsecRule

def read_modsecurity_conf():
    """Read ModSecurity configuration and check for changes"""
    session = Session()
    try:
        with open(MODSECURITY_CONF_PATH, 'r') as f:
            content = f.read()
        
        # Track changes using the config tracking function
        track_config_content(session, 'modsecurity', content)
        
        # Get config status from database
        config = session.query(ModsecRule).filter_by(rule_code='CONFIG_MODSEC').first()

        return {
            'content': content,
            'changed': config.is_content_change if config else False
        }
    finally:
        session.close()

def read_crs_conf():
    """Read CRS configuration and check for changes"""
    session = Session()
    try:
        with open(CRS_CONF_PATH, 'r') as f:
            content = f.read()
        
        # Track changes using the config tracking function
#        track_config_change(session, 'crs', content)
        
        # Get config status from database
        config = session.query(ModsecRule).filter_by(rule_code='CONFIG_CRS').first()

        return {
            'content': content,
            'changed': config.is_content_change if config else False
        }
    finally:
        session.close()

def save_modsecurity_conf(content):
    """Save ModSecurity configuration"""
    try:
        with open(MODSECURITY_CONF_PATH, 'w') as f:
            f.write(content)
        
        session = Session()
        track_config_content(session, 'modsecurity', content)
        session.close()
        return True
    except Exception as e:
        print(f"Error saving modsecurity.conf: {e}")
        return False

def save_crs_conf(content):
    """Save CRS configuration"""
    try:
        with open(CRS_CONF_PATH, 'w') as f:
            f.write(content)
        
        session = Session()
        track_config_content(session, 'crs', content)
        session.close()
        return True
    except Exception as e:
        print(f"Error saving crs-setup.conf: {e}")
        return False
