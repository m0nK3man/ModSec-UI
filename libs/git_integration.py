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

        # Check for renamed files
        all_files = {entry.rule_path: entry for entry in modified_entries}
        for entry in modified_entries:
            # Determine the current file path based on rule_code
            if entry.rule_code == 'CONFIG_MODSEC':
                current_file_path = MODSECURITY_CONF_PATH
            elif entry.rule_code == 'CONFIG_CRS':
                current_file_path = CRS_CONF_PATH
            else:
                current_file_path = os.path.join(MODSECURITY_RULES_DIR, entry.rule_path)

            # Check if the file exists
            if not os.path.exists(current_file_path):
                # File does not exist, check if it has been renamed
                for file_name in os.listdir(MODSECURITY_RULES_DIR):
                    if file_name != entry.rule_path and file_name.startswith(entry.rule_path.split('.')[0]):
                        # A file with a similar name exists, assume it has been renamed
                        new_rule_path = file_name
                        # Update the entry in the database
                        entry.rule_path = new_rule_path
                        entry.is_modified = True  # Mark as modified
                        print(f"Detected rename: {entry.rule_path} -> {new_rule_path}")
                        break

        # Re-query modified entries after checking for renames
        modified_entries = session.query(ModsecRule).filter_by(is_modified=True).all()

        if not modified_entries:
            return True  # No changes to commit

        repo = _get_repo()

        # Add changed files to git
        for entry in modified_entries:
            # Determine relative path based on rule_code
            if entry.rule_code == 'CONFIG_MODSEC':
                relative_path = os.path.relpath(MODSECURITY_CONF_PATH, GIT_REPO_PATH)
                file_path = MODSECURITY_CONF_PATH
            elif entry.rule_code == 'CONFIG_CRS':
                relative_path = os.path.relpath(CRS_CONF_PATH, GIT_REPO_PATH)
                file_path = CRS_CONF_PATH
            else:
                rule_path = os.path.join(MODSECURITY_RULES_DIR, entry.rule_path)
                relative_path = os.path.relpath(rule_path, GIT_REPO_PATH)
                file_path = rule_path  # Set file_path for content hash update

            # Add the file to the git index
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
            with open(file_path, "rb") as file:
                entry.original_content_hash = entry.content_hash
                entry.content_hash = hashlib.md5(file.read()).hexdigest()  # Save the new hash
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

