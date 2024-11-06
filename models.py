from flask_login import UserMixin
from libs.config import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'modsec_users'

    id = db.Column(db.Integer, primary_key=True)  # Ensure this is correct
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class ModsecRule(db.Model):
    __tablename__ = 'modsec_rules'

    id = db.Column(db.Integer, primary_key=True)
    rule_code = db.Column(db.String(10), nullable=False)
    rule_name = db.Column(db.String(100), nullable=False)
    rule_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    content_hash = db.Column(db.String(32))
    is_modified = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.now)
