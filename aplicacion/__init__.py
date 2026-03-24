import os
from flask import Flask
from aplicacion.extensiones import db, login_manager

def crear_aplicacion():
    """Patrón Factory para inicializar de forma segura la App de Flask."""
    app = Flask(__name__, template_folder='plantillas', static_folder='estaticos')
    app.config['SECRET_KEY'] = 'mundial2026_pro_key_nueva_arquitectura'
    
    # Configuración de Base de Datos para Railway (PostgreSQL) o Local (SQLite)
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url if db_url else 'sqlite:///' + os.path.join(basedir, 'polla_mundial_v2.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar las extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'autenticacion.login'

    with app.app_context():
        # Importar los modelos para que SQLAlchemy los reconozca y cree las tablas
        from aplicacion import modelos
        db.create_all()
        
    # Registrar Blueprints
    from aplicacion.rutas.autenticacion import autenticacion_bp
    from aplicacion.rutas.principal import principal_bp
    from aplicacion.rutas.pollas import pollas_bp
    from aplicacion.rutas.predicciones import predicciones_bp
    
    app.register_blueprint(autenticacion_bp)
    app.register_blueprint(principal_bp)
    app.register_blueprint(pollas_bp)
    app.register_blueprint(predicciones_bp)

    return app

# Funciones globales como cargar usuario para user_loader
@login_manager.user_loader
def load_user(user_id):
    from aplicacion.modelos import Usuario
    return Usuario.query.get(int(user_id))
