from config import db
from models import User
from werkzeug.security import generate_password_hash
from app import app

def create_user(username, password):
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: create_user.py <username> <password>")
    else:
        with db.app.app_context():  # Ensure app context is used
            create_user(sys.argv[1], sys.argv[2])
