# routes/configuration.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from modsec_manager.configuration_func import read_modsecurity_conf, save_modsecurity_conf, read_crs_conf, save_crs_conf
from libs.git_integration import commit_changes
from flask_login import login_required

bp = Blueprint('configuration', __name__)

@bp.route('/configuration', methods=['GET'])
@login_required
def configuration():
    view_mode = request.args.get('view_mode', session.get('view_mode', 'view'))
    session['view_mode'] = view_mode
    modsecurity_conf = read_modsecurity_conf()
    crs_conf = read_crs_conf()
    return render_template('configuration.html', 
                         modsecurity_conf=modsecurity_conf, 
                         crs_conf=crs_conf,
                         view_mode=view_mode)

@bp.route('/save_modsecurity_conf', methods=['POST'])
@login_required
def modsecurity_conf():
    if session.get('view_mode') == 'view':
        flash("Cannot modify configuration in view mode!","error")
        return redirect(url_for('configuration.configuration'))
        
    modsecurity_conf_content = request.form.get('modsecurity_conf')
    if save_modsecurity_conf(modsecurity_conf_content):
        flash("ModSecurity configuration saved successfully.","success")
    else:
        flash("Failed to save ModSecurity configuration.","error")
    return redirect(url_for('configuration.configuration'))

@bp.route('/save_crs_conf', methods=['POST'])
@login_required
def crs_conf():
    if session.get('view_mode') == 'view':
        flash("Cannot modify configuration in view mode!","error")
        return redirect(url_for('configuration.configuration'))
        
    crs_conf_content = request.form.get('crs_conf')
    if save_crs_conf(crs_conf_content):
        flash("CRS configuration saved successfully.","success")
    else:
        flash("Failed to save CRS configuration.","error")
    return redirect(url_for('configuration.configuration'))

@bp.route('/commit_config_changes', methods=['POST'])
@login_required
def commit_changes_view():
    if commit_changes():
        flash("Changes committed successfully!","success")
    else:
        flash("Error committing changes!", "error")
    return redirect(url_for('configuration.configuration'))
