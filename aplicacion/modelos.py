from aplicacion.extensiones import db
from flask_login import UserMixin
from datetime import datetime

# ==========================================
# MODELOS DE BASE DE DATOS (POLLA MUNDIAL 2026)
# ==========================================

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=True) # Nullable para usuarios que entren SOLO con Google
    correo = db.Column(db.String(120), unique=True, nullable=False) # CORREO OBLIGATORIO
    es_superadmin = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    proveedor_oauth = db.Column(db.String(50), nullable=True) # Ej: 'google', 'microsoft'
    id_oauth = db.Column(db.String(100), unique=True, nullable=True) # ID proveedor
    comentarios = db.Column(db.Text, nullable=True)

class Torneo(db.Model):
    __tablename__ = 'torneos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer)
    estado = db.Column(db.String(20), default='Activo')
    proveedor_api = db.Column(db.String(50), default='manual') # ej. 'sportmonks', 'footballdata'
    api_torneo_id = db.Column(db.String(50)) # El ID en la respectiva API
    comentarios = db.Column(db.Text, nullable=True)
    
class Polla(db.Model):
    __tablename__ = 'pollas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    es_publica = db.Column(db.Boolean, default=False)
    requiere_votacion_reglas = db.Column(db.Boolean, default=False)
    jugadores_pueden_proponer = db.Column(db.Boolean, default=False)
    comentarios = db.Column(db.Text, nullable=True)

class ParticipantePolla(db.Model):
    __tablename__ = 'participantes_polla'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), primary_key=True)
    es_administrador_polla = db.Column(db.Boolean, default=False)
    campeon_pred = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    subcampeon_pred = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    tercer_puesto_pred = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    goleador_pred = db.Column(db.Integer, db.ForeignKey('candidatos_goleador.id'), nullable=True)
    comentarios = db.Column(db.Text, nullable=True)

class CandidatoGoleador(db.Model):
    __tablename__ = 'candidatos_goleador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    estado = db.Column(db.String(20), default='Activo')


class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    bandera_url = db.Column(db.String(255), nullable=True)
    grupo_torneo = db.Column(db.String(10), nullable=True)
    comentarios = db.Column(db.Text, nullable=True)

class Partido(db.Model):
    __tablename__ = 'partidos'
    id = db.Column(db.Integer, primary_key=True)
    # ... assuming the rest of the lines are unchanged ...
    # Wait, the file has 136 lines, I can't just replace the end with ellipsis if I don't know the content.
    # Ah, I should use a more precise replacement or append.
    # Let me actually read the trailing lines of modelos.py to append properly.
    __tablename__ = 'partidos'
    id = db.Column(db.Integer, primary_key=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    equipo_local_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    equipo_visitante_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    goles_local_real = db.Column(db.Integer, nullable=True)
    goles_visitante_real = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(50), default='No Iniciado')
    jornada = db.Column(db.String(50), nullable=True)
    comentarios = db.Column(db.Text, nullable=True)

class PartidoPolla(db.Model):
    __tablename__ = 'partidos_polla'
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), primary_key=True)
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), primary_key=True)
    comentarios = db.Column(db.Text, nullable=True)

class Prediccion(db.Model):
    __tablename__ = 'predicciones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), nullable=False)
    goles_local_pred = db.Column(db.Integer, nullable=False)
    goles_visitante_pred = db.Column(db.Integer, nullable=False)
    fecha_prediccion = db.Column(db.DateTime, default=datetime.utcnow)
    comentarios = db.Column(db.Text, nullable=True)

class ConfiguracionReglaPolla(db.Model):
    __tablename__ = 'configuracion_reglas_polla'
    id = db.Column(db.Integer, primary_key=True)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=False)
    tipo_regla = db.Column(db.String(100), nullable=False)
    puntos_asignados = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), default='Aprobada')
    comentarios = db.Column(db.Text, nullable=True)

class VotoRegla(db.Model):
    __tablename__ = 'votos_reglas'
    id = db.Column(db.Integer, primary_key=True)
    regla_id = db.Column(db.Integer, db.ForeignKey('configuracion_reglas_polla.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    voto_favorable = db.Column(db.Boolean, nullable=False)
    comentarios = db.Column(db.Text, nullable=True)

class PuntosPartido(db.Model):
    __tablename__ = 'puntos_partido'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), nullable=False)
    regla_aplicada_id = db.Column(db.Integer, db.ForeignKey('configuracion_reglas_polla.id'), nullable=False)
    puntos_sumados = db.Column(db.Integer, nullable=False)
    comentarios = db.Column(db.Text, nullable=True)

class PosicionesPolla(db.Model):
    __tablename__ = 'posiciones_polla'
    id = db.Column(db.Integer, primary_key=True)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    puntos_totales = db.Column(db.Integer, default=0)
    posicion_ranking = db.Column(db.Integer, nullable=True)
    comentarios = db.Column(db.Text, nullable=True)

class LogAuditoria(db.Model):
    __tablename__ = 'logs_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    accion = db.Column(db.String(255), nullable=False)
    entidad_afectada = db.Column(db.String(100), nullable=True)
    detalle_json = db.Column(db.Text, nullable=True)
    direccion_ip = db.Column(db.String(50), nullable=True)
    comentarios = db.Column(db.Text, nullable=True)

class CodigoInvitacion(db.Model):
    __tablename__ = 'codigos_invitacion'
    id = db.Column(db.Integer, primary_key=True)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    correo_destino = db.Column(db.String(120), nullable=True)
    usado = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True) # Quién lo canjeó efectivamente
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_uso = db.Column(db.DateTime, nullable=True)

# ==========================================
# MODELOS PARA TRIVIA DIARIA E INTELIGENCIA ARTIFICIAL
# ==========================================

class ConfiguracionGlobal(db.Model):
    __tablename__ = 'configuracion_global'
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)

class PreguntaTrivia(db.Model):
    __tablename__ = 'preguntas_trivia'
    id = db.Column(db.Integer, primary_key=True)
    fecha_para_mostrar = db.Column(db.Date, unique=True, nullable=False)
    pregunta = db.Column(db.Text, nullable=False)
    opcion_a = db.Column(db.String(255), nullable=False)
    opcion_b = db.Column(db.String(255), nullable=False)
    opcion_c = db.Column(db.String(255), nullable=False)
    opcion_d = db.Column(db.String(255), nullable=False)
    opcion_correcta = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D'
    explicacion = db.Column(db.Text, nullable=True)
    proveedor_generador = db.Column(db.String(50), nullable=True) # ej. 'openai', 'gemini'
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)

class RespuestaTriviaUsuario(db.Model):
    __tablename__ = 'respuestas_trivia_usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    polla_id = db.Column(db.Integer, db.ForeignKey('pollas.id'), nullable=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_trivia.id'), nullable=False)
    opcion_elegida = db.Column(db.String(1), nullable=False)
    es_correcta = db.Column(db.Boolean, nullable=False)
    puntos_obtenidos = db.Column(db.Integer, default=0)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)
