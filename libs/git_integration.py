import os
import git
from datetime import datetime
from libs.database import Session, track_rule_change, track_config_change
from models import ModsecRule
from libs.var import *

def _get_repo():
    """Initialize or get the Git repository"""
    try:
        return git.Repo(GIT_REPO_PATH)
    except git.exc.InvalidGitRepositoryError:
        # Initialize new repository if it doesn't exist
        return git.Repo.init(GIT_REPO_PATH)

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

        # Reset modification flags and update content hash
        for entry in modified_entries:
            entry.original_content_hash = entry.content_hash  # Update original hash
            entry.content_hash = hashlib.md5(open(os.path.join(MODSECURITY_RULES_DIR, entry.rule_path), "rb").read()).hexdigest()  # Save the new hash
            entry.is_modified = False  # Reset modified flag
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

