from flask_login import UserMixin
from libs.config import db

class User(UserMixin, db.Model):
    __tablename__ = 'modsec_users'

    id = db.Column(db.Integer, primary_key=True)  # Ensure this is correct
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

