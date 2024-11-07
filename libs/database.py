from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection
engine = create_engine('postgresql://modsec_admin:bravo123@localhost/modsec_ui')
Session = sessionmaker(bind=engine)

db = SQLAlchemy()
login_manager = LoginManager()
