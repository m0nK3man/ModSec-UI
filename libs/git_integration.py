import os
import git
import hashlib
from datetime import datetime
from libs.database import Session
from models import ModsecRule
from libs.var import *

def push_changes():
    """Push committed changes to the remote Git repository"""
    try:
        repo = _get_repo()
        # Ensure the remote is set (you might want to customize the remote name)
        remote_name = 'origin'
        remote = repo.remote(remote_name)
        
        # Push changes to the remote repository
        remote.push()
        print(f"Successfully pushed changes to {remote_name}.")
        return True

    except Exception as e:
        print(f"Error pushing changes: {e}")
        return False

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
            # Determine the file path based on rule_code
            if entry.rule_code == 'CONFIG_MODSEC':
                file_path = MODSECURITY_CONF_PATH
            elif entry.rule_code == 'CONFIG_CRS':
                file_path = CRS_CONF_PATH
            else:
                file_path = os.path.join(MODSECURITY_RULES_DIR, entry.rule_path)

            # Add the file to the git index
            repo.index.add([file_path])

        # Create commit
        commit_message = _create_commit_message(modified_entries)
        repo.index.commit(
            commit_message,
            author=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL),
            committer=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL)
        )

        # Reset modification flags
        for entry in modified_entries:
            entry.is_modified = False  # Reset modified flag
            entry.content_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()  # Update hash

        session.commit()
        return True

    except Exception as e:
        print(f"Error committing changes: {e}")
        return False
    finally:
        session.close()

def _get_repo():
    """Initialize or get the Git repository"""
    try:
        return git.Repo(GIT_REPO_PATH)
    except git.exc.InvalidGitRepositoryError:
        # Initialize new repository if it doesn't exist
        return git.Repo.init(GIT_REPO_PATH)

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

