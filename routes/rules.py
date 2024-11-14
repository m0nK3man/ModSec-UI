# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from modsec_manager.rules_func import list_rules, toggle_rule, save_rule
from libs.git_integration import commit_changes, push_changes
from flask_login import login_required

bp = Blueprint('rules', __name__)

@bp.route('/rules')
@login_required
def rules():
    # Get view_mode from query parameter, fallback to session, then default to 'view'
    view_mode = request.args.get('view_mode', session.get('view_mode', 'view'))
    # Store the current view_mode in session
    session['view_mode'] = view_mode
    all_rules = list_rules()

    save_change=False
    for rule in all_rules:
        if rule['changed']:
            save_change=True
    return render_template('rules.html',
                         all_rules=all_rules,
                         save_change=save_change,
                         view_mode=view_mode)

@bp.route('/toggle_rule/<filename>')
@login_required
def toggle_rule_view(filename):
    view_mode = session.get('view_mode', 'view')
    if view_mode == 'view':
        flash("Cannot modify rules in view mode!","error")
        return redirect(url_for('rules.rules'))

    all_rules = list_rules()

    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if rule:
        toggle_rule(filename, not rule['enabled'])
        flash(f"Rule '{filename}' {'enabled' if not rule['enabled'] else 'disabled'} successfully!","success")
    return redirect(url_for('rules.rules'))

@bp.route('/edit_rule/<filename>', methods=['GET', 'POST'])
@login_required
def edit_rule(filename):
    view_mode = session.get('view_mode', 'view')
    if view_mode == 'view':
        flash("Cannot edit rules in view mode!","error")
        return redirect(url_for('rules.rules'))

    all_rules = list_rules()

    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if not rule:
        flash("Rule not found!","error")
        return redirect(url_for('rules.rules'))

    if request.method == 'POST':
        content = request.form['content']
        save_rule(filename, content)
        flash(f"Rule '{filename}' updated successfully.","success")
        return redirect(url_for('rules.rules'))

    return render_template('rule_editor.html', rule=rule)

@bp.route('/commit_changes', methods=['POST'])
@login_required
def commit_changes_view():
    if commit_changes():
        if push_changes():
            flash("Changes pushed successfully!","success")
        else:
            flash("Changes committed, but push failed!","error") 
    else:
        flash("Error committing changes!", "error")
    return redirect(url_for('home.home'))
