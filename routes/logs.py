# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from libs.elasticsearch_client import ElasticsearchClient
from libs.var import TIME_RANGES, LOGS_CONFIG, SEVERITY_LEVELS
from flask_login import login_required
import json
from datetime import datetime
import pytz

bp = Blueprint('logs', __name__)

es_client = ElasticsearchClient()

@bp.before_app_request
def initialize_config():
    """Initialize logs configuration"""
    current_app.config['LOGS_CONFIG'] = LOGS_CONFIG
    current_app.config['TIME_RANGES'] = TIME_RANGES
    current_app.config['SEVERITY_LEVELS'] = SEVERITY_LEVELS

@bp.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    try:
        # Get logs and statistics
        time_range = request.args.get('time_range', LOGS_CONFIG['DEFAULT_TIME_RANGE'])
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        logs = es_client.get_logs(time_range=time_range, search_query=search_query, start_time=start_time, end_time=end_time)
        stats = es_client.get_stats(time_range=time_range, start_time=start_time, end_time=end_time)

        severity_mapping = {
            '0': 'Emergency',
            '1': 'Alert',
            '2': 'Critical',
            '3': 'Error',
            '4': 'Warning',
            '5': 'Notice',
            '6': 'Info',
            '7': 'Debug'
        }

        # mapping severity
        for entry in stats['severity_breakdown']:
            entry['severity'] = severity_mapping.get(entry['key'], 'UNKNOWN')
        for log in logs:
            log['severity'] = severity_mapping.get(log['severity'], 'UNKNOWN')

        # Pass configuration to template
        config = {
            'time_ranges': TIME_RANGES,
            'severity_levels': SEVERITY_LEVELS,
            'logs_config': LOGS_CONFIG
        }
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('logs.logs'))

    # Convert UTC time to UTC+7
    utc_zone = pytz.utc
    tz_utc7 = pytz.timezone('Asia/Bangkok')
    for log in logs:
        # Assuming the timestamp is in ISO format, you need to parse it and convert
        log['timestamp'] = convert_to_utc7(log['timestamp'], utc_zone, tz_utc7)

    return render_template('logs.html',
                           logs=logs,
                           stats=stats,
                           time_range=time_range,
                           search_query=search_query,
                           config=config)

def convert_to_utc7(timestamp_str, utc_zone, target_zone):
    # Parse the timestamp string to datetime object with milliseconds
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Localize to UTC and then convert to target timezone (UTC+7)
    timestamp = utc_zone.localize(timestamp)  # Localize to UTC
    timestamp_utc7 = timestamp.astimezone(target_zone)  # Convert to UTC+7

    # Return the formatted timestamp
    return timestamp_utc7.strftime("%Y-%m-%d %H:%M:%S")

