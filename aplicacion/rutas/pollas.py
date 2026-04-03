from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
import hashlib
import random
import string
import socket
from datetime import datetime
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import Polla, Torneo, ParticipantePolla, ConfiguracionReglaPolla, Usuario, CodigoInvitacion, Partido, VotoRegla
from aplicacion.utilidades.correo import enviar_invitacion_polla

pollas_bp = Blueprint('pollas', __name__, url_prefix='/pollas')

def obtener_ip_local():
    """Obtiene la dirección IP en la red local (LAN) de este equipo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generar_token_polla(polla_id):
    secret = current_app.config.get('SECRET_KEY', 'mundial_super_secreto')
    return hashlib.sha256(f"polla_{polla_id}_{secret}".encode()).hexdigest()[:12]

@pollas_bp.record_once
def on_load(state):
    state.app.jinja_env.globals.update(generar_token_polla=generar_token_polla)

@pollas_bp.route('/')
@login_required
def index():
    participaciones = ParticipantePolla.query.filter_by(usuario_id=current_user.id).all()
    pollas_id = [p.polla_id for p in participaciones]
    mis_pollas = Polla.query.filter(Polla.id.in_(pollas_id)).all()
    pollas_publicas = Polla.query.filter_by(es_publica=True).filter(~Polla.id.in_(pollas_id)).all()
    return render_template('pollas/index.html', mis_pollas=mis_pollas, pollas_publicas=pollas_publicas)

@pollas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    torneo_mundial = Torneo.query.filter_by(nombre="Mundial 2026").first()
    if not torneo_mundial:
        torneo_mundial = Torneo(nombre="Mundial 2026", ano=2026, estado="Activo", comentarios="Mundial 2026")
        db.session.add(torneo_mundial)
        db.session.commit()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        es_publica = request.form.get('es_publica') == 'on'
        requiere_votacion = request.form.get('requiere_votacion') == 'on'
        permitir_propuestas = request.form.get('permitir_propuestas') == 'on'
        
        nueva_polla = Polla(
            nombre=nombre, descripcion=descripcion, torneo_id=torneo_mundial.id,
            creador_id=current_user.id, es_publica=es_publica,
            requiere_votacion_reglas=requiere_votacion, jugadores_pueden_proponer=permitir_propuestas
        )
        db.session.add(nueva_polla)
        db.session.commit()
        
        admin_participante = ParticipantePolla(usuario_id=current_user.id, polla_id=nueva_polla.id, es_administrador_polla=True)
        db.session.add(admin_participante)
        
        estado_inicial = 'Propuesta' if requiere_votacion else 'Aprobada'
        reglas_base = [
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Exacto (Pleno)", puntos_asignados=5, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Ganador (Tendencia)", puntos_asignados=3, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Goles de un Equipo", puntos_asignados=1, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Diferencia de Goles", puntos_asignados=2, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acertar el Campeón", puntos_asignados=10, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acertar el Subcampeon", puntos_asignados=7, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acertar el Tercer Puesto", puntos_asignados=5, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Atinar los 3 del Podio", puntos_asignados=15, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Trivia Diaria (Módulo IA)", puntos_asignados=2, estado=estado_inicial),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acertar Goleador del Mundial", puntos_asignados=10, estado=estado_inicial),
        ]
        db.session.bulk_save_objects(reglas_base)
        db.session.commit()
        return redirect(url_for('pollas.detalle', id=nueva_polla.id))
        
    return render_template('pollas/crear.html', torneos=[torneo_mundial])

@pollas_bp.route('/<int:id>')
@login_required
def detalle(id):
    polla = Polla.query.get_or_404(id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    
    if not polla.es_publica and not participante:
        flash("Debes usar un código de invitación.", "danger")
        return redirect(url_for('pollas.index'))

    # Deadlines y Escrutinio
    partido_inaugural = Partido.query.filter_by(torneo_id=polla.torneo_id).order_by(Partido.fecha_hora.asc()).first()
    deadline_gobernanza = None
    if partido_inaugural:
        from datetime import timedelta
        deadline_gobernanza = partido_inaugural.fecha_hora - timedelta(days=2)
    
    ahora = datetime.utcnow()
    gobernanza_cerrada = deadline_gobernanza and ahora >= deadline_gobernanza

    participantes = ParticipantePolla.query.filter_by(polla_id=id).all()
    reglas = ConfiguracionReglaPolla.query.filter_by(polla_id=id).all()

    if gobernanza_cerrada and polla.requiere_votacion_reglas:
        tipos = db.session.query(ConfiguracionReglaPolla.tipo_regla).filter_by(polla_id=id).distinct().all()
        for (t_regla,) in tipos:
            opciones = ConfiguracionReglaPolla.query.filter_by(polla_id=id, tipo_regla=t_regla).all()
            if len(opciones) > 1:
                ganadora = None
                max_votos = -1
                for opt in opciones:
                    votos = VotoRegla.query.filter_by(regla_id=opt.id).all()
                    puntos_voto = 0
                    for v in votos:
                        es_v_admin = any(p.usuario_id == v.usuario_id and p.es_administrador_polla for p in participantes)
                        puntos_voto += 2 if es_v_admin else 1
                    if puntos_voto > max_votos:
                        max_votos = puntos_voto
                        ganadora = opt
                for opt in opciones:
                    opt.estado = 'Aprobada' if opt == ganadora else 'Rechazada'
        db.session.commit()

    reglas_aprobadas = [r for r in reglas if r.estado == 'Aprobada' or (not polla.requiere_votacion_reglas and r.estado != 'Rechazada')]
    reglas_propuestas = [r for r in reglas if r.estado == 'Propuesta' and not gobernanza_cerrada]
    
    codigos_activos = CodigoInvitacion.query.filter_by(polla_id=id, usado=False).all() if (participante and participante.es_administrador_polla) else []
    usuarios_dict = {u.id: u.nombre_usuario for u in Usuario.query.all()}
    
    return render_template('pollas/detalle.html', polla=polla, es_miembro=(participante is not None), es_admin=(participante and participante.es_administrador_polla), participantes=participantes, reglas_aprobadas=reglas_aprobadas, reglas_propuestas=reglas_propuestas, usuarios_dict=usuarios_dict, codigos_activos=codigos_activos, ip_local=obtener_ip_local(), VotoRegla=VotoRegla, current_user=current_user, ahora=ahora, deadline_gobernanza=deadline_gobernanza, gobernanza_cerrada=gobernanza_cerrada)

@pollas_bp.route('/<int:id>/unirse', methods=['POST'])
@login_required
def unirse(id):
    polla = Polla.query.get_or_404(id)
    codigo = request.form.get('codigo_invitacion', '').strip().upper()
    codigo_obj = CodigoInvitacion.query.filter_by(codigo=codigo, polla_id=id, usado=False).first()
    if codigo_obj:
        nuevo = ParticipantePolla(usuario_id=current_user.id, polla_id=id, es_administrador_polla=False)
        db.session.add(nuevo)
        codigo_obj.usado = True
        db.session.commit()
        flash("Te has unido.", "success")
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/<int:id>/generar_codigo', methods=['POST'])
@login_required
def generar_codigo(id):
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    if participante and participante.es_administrador_polla:
        correo = request.form.get('correo_destino', '').strip()
        caracteres = string.ascii_uppercase + string.digits
        nuevo_c = ''.join(random.choices(caracteres, k=3)) + '-' + ''.join(random.choices(caracteres, k=4))
        inv = CodigoInvitacion(polla_id=id, codigo=nuevo_c, correo_destino=correo if correo else None)
        db.session.add(inv)
        db.session.commit()
        flash(f"Código generado: {nuevo_c}", "success")
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/invitacion/<code>')
def invitacion(code):
    codigo_obj = CodigoInvitacion.query.filter_by(codigo=code.upper(), usado=False).first()
    if not codigo_obj: return redirect(url_for('principal.index'))
    if not current_user.is_authenticated:
        session['invitacion_codigo'] = codigo_obj.codigo
        return redirect(url_for('autenticacion.registro'))
    nuevo = ParticipantePolla(usuario_id=current_user.id, polla_id=codigo_obj.polla_id)
    db.session.add(nuevo)
    codigo_obj.usado = True
    db.session.commit()
    return redirect(url_for('pollas.detalle', id=codigo_obj.polla_id))

@pollas_bp.route('/<int:id>/reglas', methods=['POST'])
@login_required
def actualizar_reglas(id):
    polla = Polla.query.get_or_404(id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    if not participante or not participante.es_administrador_polla or polla.requiere_votacion_reglas:
        flash("No permitido.", "danger")
        return redirect(url_for('pollas.detalle', id=id))
    for key, value in request.form.items():
        if key.startswith('regla_'):
            regla = ConfiguracionReglaPolla.query.filter_by(id=int(key.split('_')[1]), polla_id=id).first()
            if regla and value.isdigit(): regla.puntos_asignados = int(value)
    db.session.commit()
    flash("Reglas actualizadas.", "success")
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/<int:id>/reglas/proponer', methods=['POST'])
@login_required
def proponer_regla(id):
    polla = Polla.query.get_or_404(id)
    if not ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first() or not polla.requiere_votacion_reglas:
        return redirect(url_for('pollas.detalle', id=id))
    tipo = request.form.get('tipo_regla')
    pts = request.form.get('puntos_asignados')
    if tipo and pts:
        nueva = ConfiguracionReglaPolla(polla_id=id, tipo_regla=tipo, puntos_asignados=int(pts), estado="Propuesta")
        db.session.add(nueva)
        db.session.commit()
        db.session.add(VotoRegla(regla_id=nueva.id, usuario_id=current_user.id, voto_favorable=True))
        db.session.commit()
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/<int:id>/reglas/<int:regla_id>/votar', methods=['POST'])
@login_required
def votar_regla(id, regla_id):
    regla_n = ConfiguracionReglaPolla.query.get_or_404(regla_id)
    votos_v = VotoRegla.query.join(ConfiguracionReglaPolla).filter(ConfiguracionReglaPolla.polla_id==id, ConfiguracionReglaPolla.tipo_regla==regla_n.tipo_regla, VotoRegla.usuario_id==current_user.id).all()
    for v in votos_v: db.session.delete(v)
    db.session.add(VotoRegla(regla_id=regla_n.id, usuario_id=current_user.id, voto_favorable=True))
    db.session.commit()
    return redirect(url_for('pollas.detalle', id=id))
