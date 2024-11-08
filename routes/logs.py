# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from libs.elasticsearch_client import ElasticsearchClient
from libs.var import TIME_RANGES, LOGS_CONFIG, SEVERITY_LEVELS
from flask_login import login_required
import json

bp = Blueprint('logs', __name__)

es_client = ElasticsearchClient()

@bp.before_app_first_request
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
        logs = es_client.get_logs(time_range=time_range, search_query=search_query)
        stats = es_client.get_stats(time_range=time_range)

        # Pass configuration to template
        config = {
            'time_ranges': TIME_RANGES,
            'severity_levels': SEVERITY_LEVELS,
            'logs_config': LOGS_CONFIG
        }
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('logs.html',
                     logs=logs,
                     stats=stats,
                     time_range=time_range,
                     search_query=search_query,
                     config=config)

@bp.route('/api/logs', methods=['GET'])
@login_required
def get_logs_api():
    try:
        time_range = request.args.get('time_range', LOGS_CONFIG['DEFAULT_TIME_RANGE'])
        search_query = request.args.get('search', None)
        size = request.args.get('size', LOGS_CONFIG['MAX_RESULTS'])

        logs = get_logs(time_range=time_range, search_query=search_query, size=size)
        return jsonify({
            'status': 'success',
            'data': logs,
            'meta': {
                'time_range': time_range,
                'search_query': search_query,
                'count': len(logs)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats_api():
    try:
        time_range = request.args.get('time_range', LOGS_CONFIG['DEFAULT_TIME_RANGE'])
        stats = get_stats(time_range=time_range)
        return jsonify({
            'status': 'success',
            'data': stats,
            'meta': {
                'time_range': time_range
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/api/download_logs', methods=['GET'])
@login_required
def download_logs():
    """Export logs as JSON file"""
    try:
        time_range = request.args.get('time_range', LOGS_CONFIG['DEFAULT_TIME_RANGE'])
        search_query = request.args.get('search', None)
        logs = get_logs(time_range=time_range, search_query=search_query)

        response = current_app.response_class(
            json.dumps(logs, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment;filename=modsec_logs_{time_range}.json'}
        )
        return response
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
