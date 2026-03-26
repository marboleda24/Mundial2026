from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
import hashlib
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import Polla, Torneo, ParticipantePolla, ConfiguracionReglaPolla, Usuario

pollas_bp = Blueprint('pollas', __name__, url_prefix='/pollas')

def generar_token_polla(polla_id):
    secret = current_app.config.get('SECRET_KEY', 'mundial_super_secreto')
    return hashlib.sha256(f"polla_{polla_id}_{secret}".encode()).hexdigest()[:12]

@pollas_bp.record_once
def on_load(state):
    state.app.jinja_env.globals.update(generar_token_polla=generar_token_polla)

def obtener_o_crear_torneo_base():
    """Función de utilidad para asegurar que haya un torneo donde jugar."""
    torneo = Torneo.query.first()
    if not torneo:
        torneo = Torneo(nombre="Mundial 2026", ano=2026, estado="Activo", comentarios="Torneo base autogenerado.")
        db.session.add(torneo)
        db.session.commit()
    return torneo

@pollas_bp.route('/')
@login_required
def index():
    # Obtener pollas donde el usuario es participante o creador
    participaciones = ParticipantePolla.query.filter_by(usuario_id=current_user.id).all()
    pollas_id = [p.polla_id for p in participaciones]
    mis_pollas = Polla.query.filter(Polla.id.in_(pollas_id)).all()
    
    pollas_publicas = Polla.query.filter_by(es_publica=True).filter(~Polla.id.in_(pollas_id)).all()
    return render_template('pollas/index.html', mis_pollas=mis_pollas, pollas_publicas=pollas_publicas)

@pollas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    # Asegurar que existe el torneo Mundial 2026
    torneo_mundial = Torneo.query.filter_by(nombre="Mundial 2026").first()
    if not torneo_mundial:
        torneo_mundial = Torneo(
            nombre="Mundial 2026", 
            ano=2026, 
            estado="Activo", 
            proveedor_api="footballdata", 
            api_torneo_id="WC", 
            comentarios="Torneo Mundial 2026 autogenerado"
        )
        db.session.add(torneo_mundial)
        db.session.commit()
    
    torneos = [torneo_mundial]  # Solo mostrar Mundial 2026
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        es_publica = request.form.get('es_publica') == 'on'
        
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return redirect(url_for('pollas.crear'))
            
        nueva_polla = Polla(
            nombre=nombre,
            descripcion=descripcion,
            torneo_id=torneo_mundial.id,  # Forzar Mundial 2026
            creador_id=current_user.id,
            es_publica=es_publica,
            comentarios="Polla creada por el usuario."
        )
        db.session.add(nueva_polla)
        db.session.commit()
        
        # El creador pasa a ser participante administrador automáticamente
        admin_participante = ParticipantePolla(
            usuario_id=current_user.id,
            polla_id=nueva_polla.id,
            es_administrador_polla=True,
            comentarios="Creador original"
        )
        db.session.add(admin_participante)
        
        # Crear reglas base automáticamente
        reglas_base = [
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Exacto", puntos_asignados=3, comentarios="Pleno de goles"),
            ConfiguracionReglaPolla(polla_id=nueva_polla.id, tipo_regla="Acierto Ganador", puntos_asignados=1, comentarios="Solo el ganador (o empate)"),
        ]
        db.session.bulk_save_objects(reglas_base)
        db.session.commit()
        
        flash("¡Polla creada exitosamente! Ahora puedes invitar amigos y afinar las reglas.", "success")
        return redirect(url_for('pollas.detalle', id=nueva_polla.id))
        
    return render_template('pollas/crear.html', torneos=torneos)

@pollas_bp.route('/<int:id>')
@login_required
def detalle(id):
    polla = Polla.query.get_or_404(id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    
    # Prevenir acceso a pollas privadas de las que no es miembro
    if not polla.es_publica and not participante:
        flash("Esta polla es privada.", "danger")
        return redirect(url_for('pollas.index'))
        
    participantes = ParticipantePolla.query.filter_by(polla_id=id).all()
    reglas = ConfiguracionReglaPolla.query.filter_by(polla_id=id).all()
    
    # Diccionario rápido para evitar múltiples queries
    usuarios_dict = {u.id: u.nombre_usuario for u in Usuario.query.all()}
    
    return render_template('pollas/detalle.html', polla=polla, es_miembro=(participante is not None), es_admin=(participante and participante.es_administrador_polla), participantes=participantes, reglas=reglas, usuarios_dict=usuarios_dict)

@pollas_bp.route('/<int:id>/unirse', methods=['POST'])
@login_required
def unirse(id):
    polla = Polla.query.get_or_404(id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    
    if not participante and polla.es_publica:
        nuevo_miembro = ParticipantePolla(
            usuario_id=current_user.id,
            polla_id=id,
            es_administrador_polla=False,
            comentarios="Se unió públicamente"
        )
        db.session.add(nuevo_miembro)
        db.session.commit()
        flash(f"Te has unido a {polla.nombre} exitosamente.", "success")
    
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/invitacion/<int:id>/<token>')
def invitacion(id, token):
    if token != generar_token_polla(id):
        flash("El enlace de invitación es inválido o ha caducado.", "danger")
        return redirect(url_for('principal.index'))
    
    polla = Polla.query.get_or_404(id)
    
    if not current_user.is_authenticated:
        session['invitacion_id'] = id
        session['invitacion_token'] = token
        flash("Crea tu cuenta o inicia sesión para unirte automáticamente a la comunidad.", "info")
        return redirect(url_for('autenticacion.registro'))
        
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    if not participante:
        nuevo_miembro = ParticipantePolla(
            usuario_id=current_user.id,
            polla_id=id,
            es_administrador_polla=False,
            comentarios="Se unió mediante enlace de invitación."
        )
        db.session.add(nuevo_miembro)
        db.session.commit()
        flash(f"¡Te has unido a {polla.nombre} exitosamente mediante invitación!", "success")
        
    session.pop('invitacion_id', None)
    session.pop('invitacion_token', None)
    
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/<int:id>/reglas', methods=['POST'])
@login_required
def actualizar_reglas(id):
    """Permite al admin de la polla actualizar los puntos de las reglas"""
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    if not participante or not participante.es_administrador_polla:
        flash("Solo los administradores pueden cambiar las reglas de forma directa.", "danger")
        return redirect(url_for('pollas.detalle', id=id))
        
    # Obtener inputs
    for key, value in request.form.items():
        if key.startswith('regla_'):
            regla_id = int(key.split('_')[1])
            regla = ConfiguracionReglaPolla.query.filter_by(id=regla_id, polla_id=id).first()
            if regla and value.isdigit():
                regla.puntos_asignados = int(value)
                
    db.session.commit()
    flash("Reglas actualizadas.", "success")
    return redirect(url_for('pollas.detalle', id=id))
