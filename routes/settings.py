# routes/settings.py
import atexit  # Add this import statement at the top of your file
from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from controller.settings_func import load_config, save_config
from libs.telegram_integration import send_alert, send_test_message
from flask_login import login_required
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

bp = Blueprint('settings', __name__)

# Load configuration
config = load_config()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def daily_alert():
    """Function to send an alert if TELEGRAM_ALERT is enabled."""
    if config.get("TELEGRAM_ALERT"):
        bot_token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            print(f"[{datetime.now()}] Error: Telegram Bot Token or Chat ID is missing.")
            return {"success": False, "message": "Bot Token or Chat ID is missing."}

        try:
            result = send_alert(bot_token, chat_id)
            if result and result.get("success"):
                print(f"[{datetime.now()}] Alert sent successfully.")
                return {"success": True, "message": "Alert sent successfully."}
            else:
                error_msg = result.get("error", "Unknown error") if result else "No response from Telegram API"
                print(f"[{datetime.now()}] Failed to send alert: {error_msg}")
                return {"success": False, "message": f"Failed to send alert: {error_msg}"}
        except Exception as e:
            print(f"[{datetime.now()}] An unexpected error occurred while sending alert: {str(e)}")
            return {"success": False, "message": f"Unexpected error: {str(e)}"}
    else:
        print(f"[{datetime.now()}] Telegram Alert is disabled.")
        return {"success": False, "message": "Telegram Alert is disabled."}

# Add job to scheduler
scheduler.add_job(
    daily_alert,                 # Function to call
    trigger='cron',              # Use cron scheduling
    hour=23,                     # At 23:00
    minute=0,                    # At minute 0
    id="daily_alert_job",        # Unique job ID
    replace_existing=True        # Replace the job if it already exists
)

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
        try:
            result = send_test_message(bot_token, chat_id)

            # Check if result is valid and contains "success"
            if result and isinstance(result, dict) and result.get("success"):
                context['success'] = "Test message sent successfully!"
            else:
                # Handle the failure and print the error if available
                error_msg = result.get('error', 'Unknown error') if result else 'No response from Telegram API'
                context['error'] = f"Failed to send test message: {error_msg}"

        except Exception as e:
            # Catch any exception that might occur during message sending
            context['error'] = f"An unexpected error occurred: {str(e)}"

        return render_template('settings.html', **context)

    # Render settings page
    return render_template('settings.html', config=config, comparison_flags=comparison_flags)

@atexit.register
def shutdown_scheduler():
    """Cleanup the scheduler jobs when the app shuts down."""
    print(f"[{datetime.now()}] Shutting down the scheduler...")
    scheduler.remove_job('daily_alert_job')
