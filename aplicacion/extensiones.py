from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Instancias compartidas para evitar dependencias circulares
db = SQLAlchemy()
login_manager = LoginManager()
