# routes/configuration.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from modsec_manager import read_modsecurity_conf, save_modsecurity_conf, read_crs_conf, save_crs_conf
from flask_login import login_required

bp = Blueprint('configuration', __name__)

@bp.route('/configuration', methods=['GET'])
@login_required
def configuration():
    modsecurity_conf = read_modsecurity_conf()
    crs_conf = read_crs_conf()
    return render_template('configuration.html', modsecurity_conf=modsecurity_conf, crs_conf=crs_conf)

# Route to save ModSecurity configuration
@bp.route('/save_modsecurity_conf', methods=['POST'])
@login_required
def modsecurity_conf():
    modsecurity_conf_content = request.form.get('modsecurity_conf')
    if save_modsecurity_conf(modsecurity_conf_content):
        flash("ModSecurity configuration saved successfully.")
    else:
        flash("Failed to save ModSecurity configuration.")
    return redirect(url_for('configuration.configuration'))

# Route to save CRS configuration
@bp.route('/save_crs_conf', methods=['POST'])
@login_required
def crs_conf():
    crs_conf_content = request.form.get('crs_conf')
    if save_crs_conf(crs_conf_content):
        flash("CRS configuration saved successfully.")
    else:
        flash("Failed to save CRS configuration.")
    return redirect(url_for('configuration.configuration'))
