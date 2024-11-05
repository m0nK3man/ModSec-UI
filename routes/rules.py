# routes/rules.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from modsec_manager import list_rules, toggle_rule, save_rule
from flask_login import login_required

bp = Blueprint('rules', __name__)

@bp.route('/rules')
@login_required
def rules():
    enabled_rules, disabled_rules = list_rules()
    return render_template('rules.html', enabled_rules=enabled_rules, disabled_rules=disabled_rules)

@bp.route('/toggle_rule/<filename>')
@login_required
def toggle_rule_view(filename):
    enabled_rules, disabled_rules = list_rules()  # Unpack the two lists properly
    all_rules = enabled_rules + disabled_rules      # Combine them to search for the rule
    
    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if rule:
        toggle_rule(filename, not rule['enabled'])
        flash(f"Rule '{filename}' {'enabled' if not rule['enabled'] else 'disabled'} successful!")
    return redirect(url_for('rules.rules'))

@bp.route('/edit_rule/<filename>', methods=['GET', 'POST'])
@login_required
def edit_rule(filename):
    enabled_rules, disabled_rules = list_rules()  # Unpack the two lists properly
    all_rules = enabled_rules + disabled_rules      # Combine them to search for the rule

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
