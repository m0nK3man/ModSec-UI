# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from modsec_manager import list_rules, toggle_rule, save_rule, commit_changes
from flask_login import login_required

bp = Blueprint('rules', __name__)

@bp.route('/rules')
@login_required
def rules():
    enabled_rules, disabled_rules = list_rules()
    view_mode = request.args.get('view_mode', 'view')  # Default to view mode
    return render_template('rules.html', 
                         enabled_rules=enabled_rules, 
                         disabled_rules=disabled_rules,
                         view_mode=view_mode)

@bp.route('/toggle_rule/<filename>')
@login_required
def toggle_rule_view(filename):
    if request.args.get('view_mode') == 'view':
        flash("Cannot modify rules in view mode!")
        return redirect(url_for('rules.rules'))
    
    enabled_rules, disabled_rules = list_rules()
    all_rules = enabled_rules + disabled_rules

    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if rule:
        toggle_rule(filename, not rule['enabled'])
        flash(f"Rule '{filename}' {'enabled' if not rule['enabled'] else 'disabled'} successfully!")
    return redirect(url_for('rules.rules'))

@bp.route('/edit_rule/<filename>', methods=['GET', 'POST'])
@login_required
def edit_rule(filename):
    if request.args.get('view_mode') == 'view':
        flash("Cannot edit rules in view mode!")
        return redirect(url_for('rules.rules'))

    enabled_rules, disabled_rules = list_rules()
    all_rules = enabled_rules + disabled_rules

    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if not rule:
        flash("Rule not found.")
        return redirect(url_for('rules.rules'))

    if request.method == 'POST':
        content = request.form['content']
        save_rule(filename, content)
        flash(f"Rule '{filename}' updated successfully.")
        return redirect(url_for('rules.rules'))

    return render_template('rule_editor.html', rule=rule)

@bp.route('/commit_changes', methods=['POST'])
@login_required
def commit_changes_view():
    if commit_changes():
        flash("Changes committed successfully!")
    else:
        flash("Error committing changes!", "error")
    return redirect(url_for('rules.rules'))
