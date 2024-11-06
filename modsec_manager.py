# modsec_manager.py
import os
import subprocess
import requests
import hashlib
import git
from datetime import datetime
from libs.var import MODSECURITY_RULES_DIR, MODSECURITY_CONF_PATH, CRS_CONF_PATH, GIT_REPO_PATH, GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import ModsecRule

# Database connection
engine = create_engine('postgresql://modsec_admin:bravo123@localhost/modsec_ui')
Session = sessionmaker(bind=engine)

# ==================== Global ====================

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
    
    session.commit()
    return True

def _get_repo():
    """Initialize or get the Git repository"""
    try:
        return git.Repo(GIT_REPO_PATH)
    except git.exc.InvalidGitRepositoryError:
        # Initialize new repository if it doesn't exist
        return git.Repo.init(GIT_REPO_PATH)

# ==================== Git Integration ====================

def commit_changes():
    """Commit all pending changes to Git repository"""
    session = Session()
    try:
        # Get all modified rules and configs
        modified_entries = session.query(ModsecRule).filter_by(is_modified=True).all()
        if not modified_entries:
            return True  # No changes to commit

        repo = _get_repo()
        
        # Add changed files to git
        for entry in modified_entries:
            if entry.rule_code == 'CONFIG_MODSEC':
                relative_path = os.path.relpath(MODSECURITY_CONF_PATH, GIT_REPO_PATH)
            elif entry.rule_code == 'CONFIG_CRS':
                relative_path = os.path.relpath(CRS_CONF_PATH, GIT_REPO_PATH)
            else:
                rule_path = os.path.join(MODSECURITY_RULES_DIR, entry.rule_path)
                relative_path = os.path.relpath(rule_path, GIT_REPO_PATH)
            
            repo.index.add([relative_path])

        # Create commit
        commit_message = _create_commit_message(modified_entries)
        repo.index.commit(
            commit_message,
            author=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL),
            committer=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL)
        )

        # Reset modification flags
        for entry in modified_entries:
            entry.is_modified = False
        session.commit()

        return True

    except Exception as e:
        print(f"Error committing changes: {e}")
        return False
    finally:
        session.close()

def _create_commit_message(modified_entries):
    """Create a detailed commit message based on database changes"""
    message = ["ModSecurity Configuration Update"]
    
    rules = [e for e in modified_entries if e.rule_code not in ['CONFIG_MODSEC', 'CONFIG_CRS']]
    configs = [e for e in modified_entries if e.rule_code in ['CONFIG_MODSEC', 'CONFIG_CRS']]
    
    if rules:
        message.append("\nModified Rules:")
        for rule in rules:
            message.append(f"- {rule.rule_path}")
    
    if configs:
        message.append("\nModified Configurations:")
        for config in configs:
            if config.rule_code == 'CONFIG_MODSEC':
                message.append("- ModSecurity main configuration")
            elif config.rule_code == 'CONFIG_CRS':
                message.append("- CRS configuration")
    
    return "\n".join(message)

def get_commit_history(max_count=10):
    """Get the commit history for the repository"""
    try:
        repo = _get_repo()
        commits = []
        for commit in repo.iter_commits(max_count=max_count):
            commits.append({
                'hash': commit.hexsha[:7],
                'message': commit.message,
                'author': commit.author.name,
                'date': datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')
            })
        return commits
    except Exception as e:
        print(f"Error getting commit history: {e}")
        return []

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

# Add file tracking functionality
_file_hashes = {}
_changed_files = set()

def _calculate_file_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def _update_file_hash(filename, content):
    _file_hashes[filename] = _calculate_file_hash(content)

def _is_file_changed(filename, content):
    if filename not in _file_hashes:
        with open(os.path.join(MODSECURITY_RULES_DIR, filename), 'r') as f:
            _update_file_hash(filename, f.read())
    return _file_hashes[filename] != _calculate_file_hash(content)

def list_rules():
    """List all rules with their change status from the database"""
    session = Session()
    enabled_rules = []
    disabled_rules = []

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
                
                if rule_info['enabled']:
                    enabled_rules.append(rule_info)
                else:
                    disabled_rules.append(rule_info)

    finally:
        session.close()

    return enabled_rules, disabled_rules

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
    """Enable or disable a rule and update rule path in database."""
    session = Session()
    try:
        # Retrieve the rule from the database
        rule = session.query(ModsecRule).filter_by(rule_path=filename).first()
        
        if rule is None:
            raise ValueError(f"No rule found with the filename {filename}")

        file_path = os.path.join(MODSECURITY_RULES_DIR, filename)

        # Determine the new filename based on the `enable` flag
        if enable:
            # Remove .disable suffix to enable
            if filename.endswith(".disable"):
                new_filename = filename[:-8]  # Remove the '.disable' suffix
                os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, new_filename))
                rule.rule_path = new_filename  # Update rule path in database
        else:
            # Add .disable suffix to disable
            if not filename.endswith(".disable"):
                new_filename = f"{filename}.disable"
                os.rename(file_path, os.path.join(MODSECURITY_RULES_DIR, new_filename))
                rule.rule_path = new_filename  # Update rule path in database

        # Commit the changes to the database
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error toggling rule: {e}")
    finally:
        session.close()

# ==================== Configuration ====================

_config_hashes = {}
_changed_configs = set()

def _update_config_hash(config_type, content):
    _config_hashes[config_type] = _calculate_file_hash(content)

def _is_config_changed(config_type, content):
    if config_type not in _config_hashes:
        if config_type == 'modsecurity':
            with open(MODSECURITY_CONF_PATH, 'r') as f:
                _update_config_hash('modsecurity', f.read())
        elif config_type == 'crs':
            with open(CRS_CONF_PATH, 'r') as f:
                _update_config_hash('crs', f.read())
    return _config_hashes[config_type] != _calculate_file_hash(content)

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
