from flask import Blueprint, render_template, request, flash, redirect, url_for
from modsec_manager.dashboard_func import get_current_mode, set_mode
from flask_login import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    current_mode = get_current_mode()
    if request.method == 'POST':
        if 'mode' in request.form:
            set_mode(request.form['mode'])
            flash('WAF mode updated.')
    return render_template('dashboard.html', current_mode=current_mode)
