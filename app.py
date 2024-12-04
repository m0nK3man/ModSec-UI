import argparse
from flask import Flask
from routes import home, configuration, rules, dashboard, auth, logs
from libs.database import db, login_manager
from models import User  # Create this file and class
from flask_moment import Moment

app = Flask(__name__)
app.secret_key = 'a3f0b8c42fa67a5de4e0b8f21d7b3a76'
moment = Moment(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://modsec_admin:bravo123@localhost/modsec_ui'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(home.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(logs.bp)
app.register_blueprint(rules.bp)
app.register_blueprint(configuration.bp)
app.register_blueprint(auth.bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    parser = argparse.ArgumentParser(description="Run the Flask application with a custom port.")
    parser.add_argument('-p', '--port', type=int, default=5000, help="Port number to run the Flask app on (default: 5000)")
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=True)
