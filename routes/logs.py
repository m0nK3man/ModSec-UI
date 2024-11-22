# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from libs.elasticsearch_client import ElasticsearchClient
from flask_login import login_required
import json
from datetime import datetime
import pytz

bp = Blueprint('logs', __name__)

es_client = ElasticsearchClient()

@bp.route('/logs', methods=['GET'])
@login_required
def redirect_to_audit_logs():
    return redirect(url_for('logs.audit_logs'))

@bp.route('/logs/audit', methods=['GET', 'POST'])
@login_required
def audit_logs():
    try:
        # Get logs and statistics
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)
        
        # Determine size based on time range
        time_diff = count_time_range(start_time, end_time)
        # Default size
        max_size = calculate_max_size(time_diff)
        
        # Get logs và query info
        logs_response = es_client.get_modsec_logs(search_query=search_query, size=max_size, start_time=start_time, end_time=end_time)
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
        if logs:
            for log in logs:
                log['severity'] = severity_mapping.get(log['severity'], 'UNKNOWN')
    
    except Exception as e:
        print(f"Error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('logs.audit_logs'))

    return render_template('audit_logs.html',
                           logs=logs,
                           current_length=current_length,
                           total_hits=total_hits)

@bp.route('/logs/access', methods=['GET', 'POST'])
@login_required
def access_logs():
    try:
        # Get logs and statistics
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        # Determine size based on time range
        time_diff = count_time_range(start_time, end_time)
        # Default size
        max_size = calculate_max_size(time_diff)

        # Get logs và query info
        logs_response = es_client.get_access_logs(search_query=search_query, size=max_size, start_time=start_time, end_time=end_time)
        logs = logs_response.get('logs', [])
        current_length = logs_response.get('current_length', 0)
        total_hits = logs_response.get('total_hits', 0)

    except Exception as e:
        print(f"Error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('logs.access_logs'))

    return render_template('access_logs.html',
                           logs=logs,
                           current_length=current_length,
                           total_hits=total_hits)

@bp.route('/logs/error', methods=['GET', 'POST'])
@login_required
def error_logs():
    try:
        # Get logs and statistics
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        # Determine size based on time range
        time_diff = count_time_range(start_time, end_time)
        # Default size
        max_size = calculate_max_size(time_diff)

        # Get logs và query info
        logs_response = es_client.get_modsec_logs(search_query=search_query, size=max_size, start_time=start_time, end_time=end_time)
        logs = logs_response.get('logs', [])
        current_length = logs_response.get('current_length', 0)
        total_hits = logs_response.get('total_hits', 0)

    except Exception as e:
        print(f"Error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('logs.error_logs'))

    return render_template('error_logs.html',
                           logs=logs,
                           current_length=current_length,
                           total_hits=total_hits)

def count_time_range(start_time, end_time):
    if start_time and end_time:
        # Convert to datetime objects
        tz_utc = pytz.UTC
        tz_utc7 = pytz.timezone('Asia/Bangkok')  # Adjust for your timezone

        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # If naive datetime (no timezone), assume UTC+7
        if start_dt.tzinfo is None:
            start_dt = tz_utc7.localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = tz_utc7.localize(end_dt)

        # Convert to UTC for comparison
        start_dt_utc = start_dt.astimezone(tz_utc)
        end_dt_utc = end_dt.astimezone(tz_utc)

        # Calculate the difference in hours
        delta = (end_dt_utc - start_dt_utc).total_seconds() / 3600
        return delta
    else:
        return 0

def calculate_max_size(time_diff):
    # Default size
    max_size = 500
    if time_diff <= 1:
        max_size = 300
    elif time_diff <= 3:
        max_size = 500
    elif time_diff <= 6:
        max_size = 800
    elif time_diff <= 12:
        max_size = 1000
    else:
        max_size = 1000
    return max_size
