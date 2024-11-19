# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from libs.elasticsearch_client import ElasticsearchClient
from flask_login import login_required
import json
from datetime import datetime
import pytz

bp = Blueprint('logs', __name__)

es_client = ElasticsearchClient()

@bp.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    try:
        # Get logs and statistics
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        logs_response = es_client.get_logs(search_query=search_query, start_time=start_time, end_time=end_time)
        logs = logs_response.get('logs', [])
        current_length = logs_response.get('current_length', 0)
        total_hits = logs_response.get('total_hits', 0)

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
        for log in logs:
            log['severity'] = severity_mapping.get(log['severity'], 'UNKNOWN')
    
    except Exception as e:
        print(f"Error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('logs.logs'))

    return render_template('logs.html',
                           logs=logs,
                           current_length=current_length,
                           total_hits=total_hits,
                           search_query=search_query)

def convert_to_utc7(timestamp_str, utc_zone, target_zone):
    # Parse the timestamp string to datetime object with milliseconds
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Localize to UTC and then convert to target timezone (UTC+7)
    timestamp = utc_zone.localize(timestamp)  # Localize to UTC
    timestamp_utc7 = timestamp.astimezone(target_zone)  # Convert to UTC+7

    # Return the formatted timestamp
    return timestamp_utc7.strftime("%Y-%m-%d %H:%M:%S")

