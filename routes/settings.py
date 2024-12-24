# routes/settings.py
from flask import Blueprint, render_template, request, redirect, url_for
from controller.settings_func import load_config, save_config
from libs.telegram_integration import send_test_message  # Import necessary modules
import json

bp = Blueprint('settings', __name__)

# Load configuration
config = load_config()

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update the config variables based on form inputs
        config["LOCAL_CONF_PATH"] = request.form.get('local_conf_path', config["LOCAL_CONF_PATH"])
        config["MODSECURITY_CONF_PATH"] = request.form.get('modsecurity_conf_path', config["MODSECURITY_CONF_PATH"])
        config["CRS_CONF_PATH"] = request.form.get('crs_conf_path', config["CRS_CONF_PATH"])
        config["MODSECURITY_RULES_DIR"] = request.form.get('modsecurity_rules_dir', config["MODSECURITY_RULES_DIR"])
        config["ELASTICSEARCH_CONFIG"]["HOST"] = request.form.get('elasticsearch_host', config["ELASTICSEARCH_CONFIG"]["HOST"])
        config["ELASTICSEARCH_CONFIG"]["USER"] = request.form.get('elasticsearch_user', config["ELASTICSEARCH_CONFIG"]["USER"])
        config["ELASTICSEARCH_CONFIG"]["PASSWORD"] = request.form.get('elasticsearch_password', config["ELASTICSEARCH_CONFIG"]["PASSWORD"])
        config["LOGS_CONFIG"]["REFRESH_INTERVAL"] = int(request.form.get('logs_refresh_interval', config["LOGS_CONFIG"]["REFRESH_INTERVAL"]))
        config["TELEGRAM_BOT_TOKEN"] = request.form.get('telegram_bot_token', config["TELEGRAM_BOT_TOKEN"])
        config["TELEGRAM_CHAT_ID"] = request.form.get('telegram_chat_id', config["TELEGRAM_CHAT_ID"])
        config["TELEGRAM_ALERT"] = request.form.get('telegram_alert') == 'on'

        # debug
        #print(config)

        # Save updated config to file
        save_config(config)
        return redirect(url_for('settings.settings'))

    # Compare the values from the form with the config values
    comparison_flags = {
        "LOCAL_CONF_PATH": config["LOCAL_CONF_PATH"] == request.args.get("local_conf_path", config["LOCAL_CONF_PATH"]),
        "MODSECURITY_CONF_PATH": config["MODSECURITY_CONF_PATH"] == request.args.get("modsecurity_conf_path", config["MODSECURITY_CONF_PATH"]),
        "CRS_CONF_PATH": config["CRS_CONF_PATH"] == request.args.get("crs_conf_path", config["CRS_CONF_PATH"]),
        "MODSECURITY_RULES_DIR": config["MODSECURITY_RULES_DIR"] == request.args.get("modsecurity_rules_dir", config["MODSECURITY_RULES_DIR"]),
        "ELASTICSEARCH_HOST": config["ELASTICSEARCH_CONFIG"]["HOST"] == request.args.get("elasticsearch_host", config["ELASTICSEARCH_CONFIG"]["HOST"]),
        "ELASTICSEARCH_USER": config["ELASTICSEARCH_CONFIG"]["USER"] == request.args.get("elasticsearch_user", config["ELASTICSEARCH_CONFIG"]["USER"]),
        "ELASTICSEARCH_PASSWORD": config["ELASTICSEARCH_CONFIG"]["PASSWORD"] == request.args.get("elasticsearch_password", config["ELASTICSEARCH_CONFIG"]["PASSWORD"]),
        "LOGS_REFRESH_INTERVAL": config["LOGS_CONFIG"]["REFRESH_INTERVAL"] == int(request.args.get("logs_refresh_interval", config["LOGS_CONFIG"]["REFRESH_INTERVAL"])),
        "TELEGRAM_BOT_TOKEN": config["TELEGRAM_BOT_TOKEN"] == request.args.get("telegram_bot_token", config["TELEGRAM_BOT_TOKEN"]),
        "TELEGRAM_CHAT_ID": config["TELEGRAM_CHAT_ID"] == request.args.get("telegram_chat_id", config["TELEGRAM_CHAT_ID"]),
        "TELEGRAM_ALERT": config["TELEGRAM_ALERT"] == request.form.get('telegram_alert', config["TELEGRAM_ALERT"])
    }

    # Handle test Telegram message action
    if request.args.get('action') == 'test_telegram':
        bot_token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            return render_template(
                'settings.html',
                config=config,
                comparison_flags=comparison_flags,
                error="Telegram Bot Token and Chat ID must be configured before sending a test message."
            )

        # Send test message
        result = send_test_message(bot_token, chat_id)
        if result["success"]:
            return render_template(
                'settings.html',
                config=config,
                comparison_flags=comparison_flags,
                success="Test message sent successfully!"
            )
        else:
            return render_template(
                'settings.html',
                config=config,
                comparison_flags=comparison_flags,
                error=f"Failed to send test message: {result['error']}"
            )

    # Render settings page
    return render_template('settings.html', config=config, comparison_flags=comparison_flags)
