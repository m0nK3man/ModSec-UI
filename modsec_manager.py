# modsec_manager.py
import os
import subprocess
import requests
import hashlib
import git
import hashlib
from datetime import datetime
from libs.var import MODSECURITY_RULES_DIR, MODSECURITY_CONF_PATH, CRS_CONF_PATH, GIT_REPO_PATH, GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL

# ==================== Global ====================

def _get_repo():
    """Initialize or get the Git repository"""
    try:
        return git.Repo(GIT_REPO_PATH)
    except git.exc.InvalidGitRepositoryError:
        # Initialize new repository if it doesn't exist
        return git.Repo.init(GIT_REPO_PATH)

def _create_commit_message():
    """Create a detailed commit message based on changes"""
    message = [""]
    
    # Add changed rules
    if _changed_files:
        message.append("Modified Rules:")
        for rule in _changed_files:
            message.append(f"- {rule}")
        message.append("")
    
    # Add changed configs
    if _changed_configs:
        message.append("Modified Configurations:")
        for config in _changed_configs:
            if config == 'modsecurity':
                message.append("- ModSecurity main configuration")
            elif config == 'crs':
                message.append("- CRS configuration")
        message.append("")
    
    return "\n".join(message)

def commit_changes():
    """Commit all changes to Git repository"""
    try:
        if not (_changed_files or _changed_configs):
            return True  # No changes to commit
        
        repo = _get_repo()
        
        # Add changed rules
        for rule in _changed_files:
            rule_path = os.path.join(MODSECURITY_RULES_DIR, rule)
            relative_path = os.path.relpath(rule_path, GIT_REPO_PATH)
            repo.index.add([relative_path])
        
        # Add changed configs
        if 'modsecurity' in _changed_configs:
            relative_path = os.path.relpath(MODSECURITY_CONF_PATH, GIT_REPO_PATH)
            repo.index.add([relative_path])
        
        if 'crs' in _changed_configs:
            relative_path = os.path.relpath(CRS_CONF_PATH, GIT_REPO_PATH)
            repo.index.add([relative_path])
        
        # Create commit with the specified author
        commit_message = _create_commit_message()
        repo.index.commit(
            commit_message,
            author=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL),
            committer=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL)
        )
        
        # Clear the change tracking sets
        _changed_files.clear()
        _changed_configs.clear()
        
        return True
        
    except Exception as e:
        print(f"Error committing changes: {e}")
        return False

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
    enabled_rules = []
    disabled_rules = []

    for filename in sorted(os.listdir(MODSECURITY_RULES_DIR)):
        if filename.endswith(".conf"):
            with open(os.path.join(MODSECURITY_RULES_DIR, filename), "r") as f:
                content = f.read()
                if filename not in _file_hashes:
                    _update_file_hash(filename, content)
                
                rule = {
                    'filename': filename,
                    'content': content,
                    'enabled': not filename.startswith("."),
                    'changed': filename in _changed_files
                }
                if rule['enabled']:
                    enabled_rules.append(rule)
                else:
                    disabled_rules.append(rule)

    return enabled_rules, disabled_rules

def save_rule(filename, content):
    with open(os.path.join(MODSECURITY_RULES_DIR, filename), "w") as f:
        f.write(content)
    
    if _is_file_changed(filename, content):
        _changed_files.add(filename)
    else:
        _changed_files.discard(filename)

# Keep other existing functions unchanged

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
    with open(MODSECURITY_CONF_PATH, 'r') as f:
        content = f.read()
        if 'modsecurity' not in _config_hashes:
            _update_config_hash('modsecurity', content)
        return {
            'content': content,
            'changed': 'modsecurity' in _changed_configs
        }

def read_crs_conf():
    with open(CRS_CONF_PATH, 'r') as f:
        content = f.read()
        if 'crs' not in _config_hashes:
            _update_config_hash('crs', content)
        return {
            'content': content,
            'changed': 'crs' in _changed_configs
        }

def save_modsecurity_conf(content):
    try:
        with open(MODSECURITY_CONF_PATH, 'w') as f:
            f.write(content)
        
        if _is_config_changed('modsecurity', content):
            _changed_configs.add('modsecurity')
        else:
            _changed_configs.discard('modsecurity')
        return True
    except Exception as e:
        print(f"Error saving modsecurity.conf: {e}")
        return False

def save_crs_conf(content):
    try:
        with open(CRS_CONF_PATH, 'w') as f:
            f.write(content)
        
        if _is_config_changed('crs', content):
            _changed_configs.add('crs')
        else:
            _changed_configs.discard('crs')
        return True
    except Exception as e:
        print(f"Error saving crs-setup.conf: {e}")
        return False
