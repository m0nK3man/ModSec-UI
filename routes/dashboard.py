# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from modsec_manager.dashboard_func import get_current_mode, set_mode
from libs.git_integration import commit_changes, push_changes
from flask_login import login_required
import json

bp = Blueprint('dashboard', __name__)

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

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('dashboard.html', 
                         current_mode=current_mode,
                         mode_changed=mode_changed)

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
