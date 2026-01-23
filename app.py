from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mundial2026_pro_key'

# Configuración de Base de Datos para Railway (PostgreSQL) o Local (SQLite)
basedir = os.path.abspath(os.path.dirname(__file__))
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url if db_url else 'sqlite:///' + os.path.join(basedir, 'polla_mundial.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
# --- CONFIGURACIÓN ---
TEAMS_FALLBACK = [
    "Argentina", "Brasil", "Francia", "Inglaterra", "España", "Alemania", "Portugal", "Países Bajos", "Italia", "Bélgica",
    "Croacia", "Uruguay", "Colombia", "México", "USA", "Marruecos", "Japón", "Senegal", "Corea del Sur", "Australia",
    "Dinamarca", "Suiza", "Ecuador", "Chile", "Perú", "Irán", "Arabia Saudita", "Canadá", "Costa Rica", "Polonia"
]

login_manager.login_view = 'login'

# --- MODELOS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    puntos = db.Column(db.Integer, default=0)

class Prediccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    partido_id = db.Column(db.Integer, nullable=False)
    goles_local = db.Column(db.Integer)
    goles_visitante = db.Column(db.Integer)

class PrediccionTorneo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    campeon = db.Column(db.String(100))
    subcampeon = db.Column(db.String(100))
    tercer_puesto = db.Column(db.String(100))

class Partido(db.Model):
    __tablename__ = 'partidos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200)) # e.g. "Argentina vs Francia"
    fecha = db.Column(db.String(50))   # e.g. "2026-06-11 15:00:00"
    local_nombre = db.Column(db.String(100))
    local_flag = db.Column(db.String(200))
    visitante_nombre = db.Column(db.String(100))
    visitante_flag = db.Column(db.String(200))
    goles_local_real = db.Column(db.Integer, nullable=True)
    goles_visitante_real = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(20)) # NS, FT, LIVE
    # Optional: Add jornada if needed, or parse from date
    # jornada = db.Column(db.String(50)) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RUTAS ---

@app.route('/')
@login_required
def index():
    # Traemos los partidos ordenados por fecha
    partidos_raw = Partido.query.order_by(Partido.fecha.asc()).all()
    
    # AGRUPAR POR JORNADA (Usando fecha como aproximación)
    agrupados = {}
    for p in partidos_raw:
        # Usar la fecha (primeros 10 caracteres: YYYY-MM-DD) como nombre de grupo
        nombre_grupo = p.fecha[:10] 
        
        # Opcional: Podrías mapear fechas a "Jornada 1", "Octavos", etc. si tuvieras esa lógica
            
        if nombre_grupo not in agrupados:
            agrupados[nombre_grupo] = []
        agrupados[nombre_grupo].append(p)
    
    # Traer predicciones del usuario logueado
    mis_predicciones = {}
    prediccion_torneo = None
    
    if current_user.is_authenticated:
        preds = Prediccion.query.filter_by(user_id=current_user.id).all()
        mis_predicciones = {p.partido_id: p for p in preds}
        prediccion_torneo = PrediccionTorneo.query.filter_by(user_id=current_user.id).first()
    
    # Obtener lista de equipos únicos para el dropdown
    equipos = set()
    keywords_exclude = ['Group', 'Winner', 'Runner', 'Por definir', 'To Be Defined', '1st', '2nd']
    
    for p in partidos_raw:
        # Check Local
        if p.local_nombre and not any(k in p.local_nombre for k in keywords_exclude):
            equipos.add(p.local_nombre)
        # Check Visitante
        if p.visitante_nombre and not any(k in p.visitante_nombre for k in keywords_exclude):
            equipos.add(p.visitante_nombre)
            
    lista_equipos = sorted(list(equipos))
    
    # Si no hay equipos (ej. inicio de temporada o error de sync), usar fallback
    if not lista_equipos:
        lista_equipos = sorted(TEAMS_FALLBACK)

    return render_template('index.html', agrupados=agrupados, predicciones=mis_predicciones, equipos=lista_equipos, prediccion_torneo=prediccion_torneo)

@app.route('/ranking')
def ranking():
    usuarios = User.query.order_by(User.puntos.desc()).all()
    return render_template('ranking.html', usuarios=usuarios)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        user = User(username=request.form['username'], 
                    password=generate_password_hash(request.form['password']))
        try:
            db.session.add(user)
            db.session.commit()
            flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Este nombre de usuario ya está en uso.', 'danger')
            print(f"Error registro: {e}")
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciales incorrectas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/pronosticar', methods=['POST'])
@login_required
def pronosticar():
    p_id = int(request.form.get('partido_id'))
    g_l = int(request.form.get('goles_local'))
    g_v = int(request.form.get('goles_visitante'))
    
    pred = Prediccion.query.filter_by(user_id=current_user.id, partido_id=p_id).first()
    if pred:
        pred.goles_local, pred.goles_visitante = g_l, g_v
    else:
        db.session.add(Prediccion(user_id=current_user.id, partido_id=p_id, goles_local=g_l, goles_visitante=g_v))
    
    db.session.commit()
    flash("Pronóstico guardado.", "success")
    return redirect(url_for('index'))

@app.route('/prediccion_torneo', methods=['POST'])
@login_required
def prediccion_torneo():
    campeon = request.form.get('campeon')
    subcampeon = request.form.get('subcampeon')
    tercero = request.form.get('tercero')
    
    pred = PrediccionTorneo.query.filter_by(user_id=current_user.id).first()
    if not pred:
        pred = PrediccionTorneo(user_id=current_user.id)
        db.session.add(pred)
    
    pred.campeon = campeon
    pred.subcampeon = subcampeon
    pred.tercer_puesto = tercero
    
    db.session.commit()
    flash("¡Tu predicción del torneo ha sido guardada!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)