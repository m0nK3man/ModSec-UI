# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from controller.dashboard_func import get_current_mode, set_mode
from libs.git_integration import commit_changes, push_changes
from libs.elasticsearch_client import ElasticsearchClient
from flask_login import login_required
import json

bp = Blueprint('dashboard', __name__)

es_client = ElasticsearchClient()

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
        search_query = request.args.get('search', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        stats = es_client.get_modsec_stats(search_query=search_query, start_time=start_time, end_time=end_time)

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

    except Exception as e:
        print(f"Error: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('dashboard.html', 
                        current_mode=current_mode,
                        save_change=mode_changed,
			            stats=stats)

@bp.route('/commit_dashboard_changes', methods=['POST'])
@login_required
def commit_changes_view():
    if commit_changes():
        if push_changes():
            # Update the original_mode in session after successful commit and push
            current_mode = get_current_mode()
            session['original_mode'] = current_mode
            flash("Changes pushed successfully!", "success")
        else:
            flash("Changes committed, but push failed!","error")
    else:
        flash("Error committing changes!", "error")
    return redirect(url_for('dashboard.dashboard'))
