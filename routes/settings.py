# routes/settings.py
from flask import Blueprint, render_template, request, redirect, url_for
from controller.settings_func import *
import json

bp = Blueprint('settings', __name__)

config = load_config()

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update the config variables based on form inputs
        config["LOCAL_CONF_PATH"] = request.form['local_conf_path']
        config["MODSECURITY_CONF_PATH"] = request.form['modsecurity_conf_path']
        config["CRS_CONF_PATH"] = request.form['crs_conf_path']
        config["MODSECURITY_RULES_DIR"] = request.form['modsecurity_rules_dir']
#        config["GIT_REPO_PATH"] = request.form['git_repo_path']
#        config["GIT_AUTHOR_NAME"] = request.form['git_author_name']
#        config["GIT_AUTHOR_EMAIL"] = request.form['git_author_email']
        config["ELASTICSEARCH_CONFIG"]["HOST"] = request.form['elasticsearch_host']
        config["ELASTICSEARCH_CONFIG"]["USER"] = request.form['elasticsearch_user']
        config["ELASTICSEARCH_CONFIG"]["PASSWORD"] = request.form['elasticsearch_password']
        config["LOGS_CONFIG"]["REFRESH_INTERVAL"] = int(request.form['logs_refresh_interval'])
        config["TELEGRAM_BOT_TOKEN"] = request.form['telegram_bot_token']
        config["TELEGRAM_CHAT_ID"] = request.form['telegram_chat_id']
        
        # Save updated config to file
        save_config(config)

        return redirect(url_for('settings.settings'))

    return render_template('settings.html', config=config)
