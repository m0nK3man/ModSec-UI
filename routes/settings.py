# routes/settings.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.settings_func import load_config, save_config
from libs.telegram_integration import send_test_message  # Import necessary modules
from flask_login import login_required
import json

bp = Blueprint('settings', __name__)

# Load configuration
config = load_config()

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
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
        config["TELEGRAM_BOT_TOKEN"] = request.form.get('telegram_bot_token', config["TELEGRAM_BOT_TOKEN"])
        config["TELEGRAM_CHAT_ID"] = request.form.get('telegram_chat_id', config["TELEGRAM_CHAT_ID"])
        config["TELEGRAM_ALERT"] = request.form.get('telegram_alert') == 'on'

        # Update Instances
        if "Instances" not in config:
            config["Instances"] = {}  # Add default if not present

        instance_names = request.form.getlist('instance_name[]')
        instance_ips = request.form.getlist('instance_ip[]')

        # Validate instances and update config
        if len(instance_names) == len(instance_ips):
            config["Instances"] = {name: ip for name, ip in zip(instance_names, instance_ips)}
        else:
            flash("Mismatch between instance names and IPs. Please check your input.", "error")
            return redirect(url_for('settings.settings'))

        # Save updated config to file
        if save_config(config):
            flash("Configuration saved successfully!", "success")
        else:
            flash("Failed to save configuration!", "error")

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
        "TELEGRAM_BOT_TOKEN": config["TELEGRAM_BOT_TOKEN"] == request.args.get("telegram_bot_token", config["TELEGRAM_BOT_TOKEN"]),
        "TELEGRAM_CHAT_ID": config["TELEGRAM_CHAT_ID"] == request.args.get("telegram_chat_id", config["TELEGRAM_CHAT_ID"]),
        "TELEGRAM_ALERT": config["TELEGRAM_ALERT"] == request.form.get('telegram_alert', config["TELEGRAM_ALERT"])
    }

    # Handle test Telegram message action
    if request.args.get('action') == 'test_telegram':
        bot_token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")

        context = {
            'config': config,
            'comparison_flags': comparison_flags
        }

        if not bot_token or not chat_id:
            context['error'] = "Telegram Bot Token and Chat ID must be configured before sending a test message."
            return render_template('settings.html', **context)

        # Send test message
        result = send_test_message(bot_token, chat_id)
        if result["success"]:
            context['success'] = "Test message sent successfully!"
        else:
            context['error'] = f"Failed to send test message: {result['error']}"

        return render_template('settings.html', **context)

    # Render settings page
    return render_template('settings.html', config=config, comparison_flags=comparison_flags)
