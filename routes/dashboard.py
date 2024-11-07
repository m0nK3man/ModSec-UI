from flask import Blueprint, render_template, request, flash, redirect, url_for
from modsec_manager.dashboard_func import get_current_mode, set_mode
from flask_login import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        # Attempt to retrieve the current mode
        current_mode = get_current_mode()
        
        if request.method == 'POST':
            if 'mode' in request.form:
                # Attempt to set the mode
                set_mode(request.form['mode'])
                flash('WAF mode updated successfully.', "success")
                
    except Exception as e:
        # Handle any exceptions that occur, logging the error and flashing a message
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    # Render the dashboard template if no exceptions occurred
    return render_template('dashboard.html', current_mode=current_mode)

