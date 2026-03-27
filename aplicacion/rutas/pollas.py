from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
import hashlib
import random
import string
import socket
from datetime import datetime
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import Polla, Torneo, ParticipantePolla, ConfiguracionReglaPolla, Usuario, CodigoInvitacion
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
        flash("Debes usar un código de invitación para ver esta polla.", "danger")
        return redirect(url_for('pollas.index'))
        
    participantes = ParticipantePolla.query.filter_by(polla_id=id).all()
    reglas = ConfiguracionReglaPolla.query.filter_by(polla_id=id).all()
    codigos_activos = CodigoInvitacion.query.filter_by(polla_id=id, usado=False).all() if (participante and participante.es_administrador_polla) else []
    
    # Diccionario rápido para evitar múltiples queries
    usuarios_dict = {u.id: u.nombre_usuario for u in Usuario.query.all()}
    ip_local = obtener_ip_local()
    
    return render_template('pollas/detalle.html', polla=polla, es_miembro=(participante is not None), es_admin=(participante and participante.es_administrador_polla), participantes=participantes, reglas=reglas, usuarios_dict=usuarios_dict, codigos_activos=codigos_activos, ip_local=ip_local)

@pollas_bp.route('/<int:id>/unirse', methods=['POST'])
@login_required
def unirse(id):
    polla = Polla.query.get_or_404(id)
    codigo_ingresado = request.form.get('codigo_invitacion', '').strip().upper()
    
    if not codigo_ingresado:
        flash("Debes ingresar un código de invitación obligatorio.", "warning")
        return redirect(url_for('pollas.detalle', id=id))

    codigo_obj = CodigoInvitacion.query.filter_by(codigo=codigo_ingresado, polla_id=id, usado=False).first()
    
    if not codigo_obj:
        flash("Código de invitación inválido, inexistente o ya ha sido utilizado.", "danger")
        return redirect(url_for('pollas.detalle', id=id))

    if codigo_obj.correo_destino and codigo_obj.correo_destino.lower() != current_user.correo.lower():
        flash(f"Este código es exclusivo para el correo: {codigo_obj.correo_destino}. No puedes canjearlo con tu cuenta actual.", "danger")
        return redirect(url_for('pollas.detalle', id=id))

    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    if not participante:
        nuevo_miembro = ParticipantePolla(
            usuario_id=current_user.id,
            polla_id=id,
            es_administrador_polla=False,
            comentarios="Se unió mediante código de un solo uso."
        )
        db.session.add(nuevo_miembro)
        
        codigo_obj.usado = True
        codigo_obj.usuario_id = current_user.id
        codigo_obj.fecha_uso = datetime.utcnow()
        
        db.session.commit()
        flash(f"¡El código fue aceptado! Te has unido a {polla.nombre} exitosamente.", "success")
    else:
        flash("Ya eres miembro de esta polla.", "info")
    
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/<int:id>/generar_codigo', methods=['POST'])
@login_required
def generar_codigo(id):
    polla = Polla.query.get_or_404(id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=id).first()
    
    if not participante or not participante.es_administrador_polla:
        flash("Solo el administrador puede generar nuevos códigos de acceso.", "danger")
        return redirect(url_for('pollas.detalle', id=id))
        
    correo_destino = request.form.get('correo_destino', '').strip()
    
    # Generar un código aleatorio seguro (Ej: X9J-4KA2)
    caracteres = string.ascii_uppercase + string.digits
    nuevo_codigo = ''.join(random.choices(caracteres, k=3)) + '-' + ''.join(random.choices(caracteres, k=4))
    
    inv_obj = CodigoInvitacion(
        polla_id=id,
        codigo=nuevo_codigo,
        correo_destino=correo_destino if correo_destino else None
    )
    db.session.add(inv_obj)
    db.session.commit()
    
    if correo_destino:
        # Reemplazar 127.0.0.1 o localhost por la IP de la red local
        enlace_path = url_for('pollas.invitacion', code=nuevo_codigo)
        enlace_lan = f"http://{obtener_ip_local()}:5000{enlace_path}"
        
        enviado, msg = enviar_invitacion_polla(correo_destino, polla.nombre, nuevo_codigo, current_user.nombre_usuario, enlace_lan)
        if enviado:
            flash(f"Se generó el código {nuevo_codigo} y fue enviado por correo a {correo_destino}.", "success")
        else:
            flash(f"El código {nuevo_codigo} fue generado, pero falló el envío del correo: {msg}", "warning")
    else:
        flash(f"Código manual generado: {nuevo_codigo}. Cópialo y compártelo de forma segura.", "success")
        
    return redirect(url_for('pollas.detalle', id=id))

@pollas_bp.route('/invitacion/<code>')
def invitacion(code):
    codigo_obj = CodigoInvitacion.query.filter_by(codigo=code.upper(), usado=False).first()
    if not codigo_obj:
        flash("El código de invitación es inválido, introducido incorrectamente o ya fue usado.", "danger")
        return redirect(url_for('principal.index'))
    
    polla = Polla.query.get_or_404(codigo_obj.polla_id)
    
    if not current_user.is_authenticated:
        session['invitacion_codigo'] = codigo_obj.codigo
        session['invitacion_polla_id'] = polla.id
        flash(f"Tienes un pase VIP para {polla.nombre}. Crea tu cuenta con el correo al que te llegó la invitación para canjear tu código de acceso automático.", "info")
        return redirect(url_for('autenticacion.registro'))

    if codigo_obj.correo_destino and codigo_obj.correo_destino.lower() != current_user.correo.lower():
        flash(f"Este enlace VIP es exclusivo para el correo: {codigo_obj.correo_destino}. Por favor, inicia sesión con la cuenta correspondiente.", "danger")
        return redirect(url_for('autenticacion.login'))
        
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=polla.id).first()
    if not participante:
        nuevo_miembro = ParticipantePolla(
            usuario_id=current_user.id,
            polla_id=polla.id,
            es_administrador_polla=False,
            comentarios="Se unió mediante enlace de invitación VIP."
        )
        db.session.add(nuevo_miembro)
        codigo_obj.usado = True
        codigo_obj.usuario_id = current_user.id
        codigo_obj.fecha_uso = datetime.utcnow()
        db.session.commit()
        flash(f"¡Te has unido a {polla.nombre} exitosamente canjeando tu código VIP!", "success")
        
    session.pop('invitacion_codigo', None)
    session.pop('invitacion_polla_id', None)
    
    return redirect(url_for('pollas.detalle', id=polla.id))

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
