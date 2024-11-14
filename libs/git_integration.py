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
        print("Called push_changes()")
        # Push changes to the remote repository
        remote.push()
        print(f"Successfully pushed changes to {remote_name}.")
        return True

    except Exception as e:
        print(f"Error pushing changes: {e}")
        return False

def commit_to_git(modified_entries):
    """Create a Git commit with a message based on modified entries."""
    repo = _get_repo()
    commit_message = _create_commit_message(modified_entries)
    repo.index.commit(
        commit_message,
        author=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL),
        committer=git.Actor(GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL)
    )

def reset_modification_flags(modified_entries):
    for entry in modified_entries:
        entry.is_modified = False
        entry.is_content_change = False

def update_content_hash(modified_entries):
    """Update content hashes for modified entries."""
    for entry in modified_entries:
        # Determine the file path for each entry
        if entry.rule_code == 'CONFIG_MODSEC':
            file_path = os.path.join(LOCAL_CONF_PATH, "modsecurity.conf")
        elif entry.rule_code == 'CONFIG_CRS':
            file_path = os.path.join(LOCAL_CONF_PATH, "crs/crs-setup.conf")
        else:
            file_path = os.path.join(LOCAL_CONF_PATH, "crs/rules", entry.rule_path)

        with open(file_path, "rb") as f:
            entry.content_hash = hashlib.md5(f.read()).hexdigest()

def rename_filepath_with_status(modified_entries):
    """Rename filepath with status for modified entries."""
    for rule in modified_entries:
        # Determine the file path for each entry
        origin_file_path = os.path.join(MODSECURITY_RULES_DIR, rule.rule_path)
        new_rule_path=rule.rule_path	
	    # mismatch: if rule is enabled and rulepath is disable -> rulepath rename to enable
        if rule.is_enabled and rule.rule_path.endswith(".disable"):
            new_rule_path = rule.rule_path[:-8] # Remove the '.disable' suffix
		
    	# mismatch: if rule is disabled and rulepath is enable -> rulepath rename to disabled
        if (not rule.is_enabled) and rule.rule_path.endswith(".conf"):
            new_rule_path = f"{rule.rule_path}.disable" # Add the '.disable' suffix

        os.rename(origin_file_path, os.path.join(MODSECURITY_RULES_DIR, new_rule_path))
        rule.rule_path = new_rule_path  # Update rule path in database

def commit_changes():
    """Orchestrate the commit process for all modified entries."""
    session = Session()
    try:
        # Step 1: Get modified entries
        modified_entries = session.query(ModsecRule).filter_by(is_modified=True).all()
        
        print("Called commit_changes()")

        if not modified_entries:
            return False

        # Step 2: Handle logic before commit
        update_content_hash(modified_entries)
        rename_filepath_with_status(modified_entries)

        # Step 3: Stage files
        os.system("git add -A")

        # Step 4: Commit to Git
        commit_to_git(modified_entries)

        # Step 5: Commit database transaction
        reset_modification_flags(modified_entries)
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
    message = [""]

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

