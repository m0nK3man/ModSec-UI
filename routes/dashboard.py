# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from modsec_manager.dashboard_func import get_current_mode, set_mode, get_logs, get_stats
from libs.git_integration import commit_changes, push_changes
from libs.var import TIME_RANGES, DASHBOARD_CONFIG, SEVERITY_LEVELS
from flask_login import login_required
import json

bp = Blueprint('dashboard', __name__)

@bp.before_app_first_request
def initialize_config():
    """Initialize dashboard configuration"""
    current_app.config['DASHBOARD_CONFIG'] = DASHBOARD_CONFIG
    current_app.config['TIME_RANGES'] = TIME_RANGES
    current_app.config['SEVERITY_LEVELS'] = SEVERITY_LEVELS

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        # Retrieve the current mode
        current_mode = get_current_mode()
        
        # Get the original mode from the session, or set it if not present
        if 'original_mode' not in session:
            session['original_mode'] = current_mode

        mode_changed = current_mode != session['original_mode']
        
        if request.method == 'POST':
            if 'mode' in request.form:
                new_mode = request.form['mode']
                if new_mode != current_mode:
                    if set_mode(new_mode):
                        flash('WAF mode updated successfully.', "success")
                        current_mode = new_mode
                        mode_changed = current_mode != session['original_mode']
                    else:
                        flash('Failed to update WAF mode.', "error")

        # Get logs and statistics
        time_range = request.args.get('time_range', DASHBOARD_CONFIG['DEFAULT_TIME_RANGE'])
        search_query = request.args.get('search', None)
        logs = get_logs(time_range=time_range, search_query=search_query)
        stats = get_stats(time_range=time_range)
        
        # Pass configuration to template
        config = {
            'time_ranges': TIME_RANGES,
            'severity_levels': SEVERITY_LEVELS,
            'dashboard_config': DASHBOARD_CONFIG
        }
                        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('dashboard.html', 
                         current_mode=current_mode,
                         mode_changed=mode_changed,
                         logs=logs,
                         stats=stats,
                         time_range=time_range,
                         search_query=search_query,
                         config=config)

@bp.route('/api/logs', methods=['GET'])
@login_required
def get_logs_api():
    try:
        time_range = request.args.get('time_range', DASHBOARD_CONFIG['DEFAULT_TIME_RANGE'])
        search_query = request.args.get('search', None)
        size = request.args.get('size', DASHBOARD_CONFIG['MAX_RESULTS'])
        
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
        time_range = request.args.get('time_range', DASHBOARD_CONFIG['DEFAULT_TIME_RANGE'])
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

@bp.route('/commit_changes', methods=['POST'])
@login_required
def commit_changes_view():
    try:
        commit_message = request.form.get('commit_message', 'Updated WAF configuration')
        
        if commit_changes(commit_message):
            if push_changes():
                flash("Changes pushed successfully!", "success")
                session['original_mode'] = get_current_mode()
            else:
                flash("Changes committed, but push failed!", "error")
        else:
            flash("Error committing changes!", "error")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
    
    return redirect(url_for('dashboard.dashboard'))

@bp.route('/api/download_logs', methods=['GET'])
@login_required
def download_logs():
    """Export logs as JSON file"""
    try:
        time_range = request.args.get('time_range', DASHBOARD_CONFIG['DEFAULT_TIME_RANGE'])
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
