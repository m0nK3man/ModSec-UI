from models import ModsecRule
import hashlib
from datetime import datetime
from libs.var import *
import os
import logging
from functools import wraps
from flask import current_app, jsonify
import traceback

def track_rule_content(session, rule_path, content):
    """Track changes to rule files in the database"""
    rule = session.query(ModsecRule).filter_by(rule_path=rule_path).first()

    # Calculate current content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    compare_content(session,rule,current_hash)
    
    return True

def track_config_content(session, config_type, content):
    """Track changes to configuration files in the database"""
    # Define config codes
    config_codes = {
        'modsecurity': 'CONFIG_MODSEC',
        'crs': 'CONFIG_CRS'
    }

    # Query the database for the configuration entry
    config = session.query(ModsecRule).filter_by(rule_code=config_codes[config_type]).first()
    
    # Calculate current content hash
    current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    compare_content(session,config,current_hash)
    
    return True

def compare_content(session, entry, current_hash):
    if entry:
        # Update modified state based on hash comparison
        entry.is_modified = (entry.content_hash != current_hash) # or entry.is_enabled != )
    else:
        # Logic to handle case where rule doesn't exist (optional)
        return False
    session.commit()  # Commit the change to is_modified only
    return True

def setup_logging(app):
    """Configure logging for the application"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # File handler
    file_handler = logging.FileHandler(os.path.join(log_dir, 'modsec_manager.log'))
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Configure elasticsearch logger
    es_logger = logging.getLogger('elasticsearch')
    es_logger.addHandler(file_handler)
    es_logger.setLevel(logging.WARNING)

def handle_errors(f):
    """Decorator for handling errors in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            
            if request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'error_type': type(e).__name__
                }), 500
            else:
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('dashboard.dashboard'))
    
    return decorated_function

class ModsecError(Exception):
    """Base exception for ModSecurity Manager"""
    pass

class ConfigurationError(ModsecError):
    """Raised when there's an error in configuration"""
    pass

class ElasticsearchError(ModsecError):
    """Raised when there's an error with Elasticsearch operations"""
    pass

class GitError(ModsecError):
    """Raised when there's an error with Git operations"""
    pass
