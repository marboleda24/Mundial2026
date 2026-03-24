from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from aplicacion.extensiones import db
from aplicacion.modelos import Usuario
import re

autenticacion_bp = Blueprint('autenticacion', __name__, url_prefix='/auth')

# Expresión regular para validar formato de correo electrónico
REGEX_CORREO = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@autenticacion_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('principal.index')) # TODO: Crear blueprint principal
        
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        nombre_usuario = request.form.get('nombre_usuario', '').strip()
        password = request.form.get('password', '')
        
        # 1. Validaciones Robusta
        if not correo or not password or not nombre_usuario:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('autenticacion.registro'))
            
        if not re.match(REGEX_CORREO, correo):
            flash('El formato del correo electrónico no es válido.', 'warning')
            return redirect(url_for('autenticacion.registro'))
            
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres para cumplir con estándares de seguridad.', 'warning')
            return redirect(url_for('autenticacion.registro'))
            
        # 2. Comprobar existencia
        usuario_existente = Usuario.query.filter((Usuario.correo == correo) | (Usuario.nombre_usuario == nombre_usuario)).first()
        if usuario_existente:
            flash('El correo o nombre de usuario ya se encuentra registrado.', 'danger')
            return redirect(url_for('autenticacion.registro'))
            
        # 3. Hashing fuerte (Por defecto werkzeug utilza scrypt en las versiones más recientes o pbkdf2:sha256)
        contrasena_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
        nuevo_usuario = Usuario(
            correo=correo, 
            nombre_usuario=nombre_usuario, 
            contrasena_hash=contrasena_hash
        )
        db.session.add(nuevo_usuario)
        
        try:
            db.session.commit()
            login_user(nuevo_usuario) # Autologin moderno
            flash('¡Registro exitoso! Bienvenido a la fiebre del fútbol.', 'success')
            
            # Recoger invitación en espera
            inv_id = session.get('invitacion_id')
            inv_token = session.get('invitacion_token')
            if inv_id and inv_token:
                return redirect(url_for('pollas.invitacion', id=inv_id, token=inv_token))
                
            return redirect(url_for('principal.index'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al procesar el registro.', 'danger')
            print(f"Error de DB en registro: {e}")

    return render_template('autenticacion/registro.html')

@autenticacion_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('principal.index'))
        
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        
        # Autenticación principal usando el correo electrónico (estándar moderno)
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        # También permitimos fallback por nombre de usuario si así lo prefieren
        if not usuario:
            usuario = Usuario.query.filter_by(nombre_usuario=correo).first()
            
        if usuario and usuario.contrasena_hash and check_password_hash(usuario.contrasena_hash, password):
            login_user(usuario)
            flash(f'¡Bienvenido de vuelta, {usuario.nombre_usuario}!', 'success')
            
            # Rescatar invitación
            inv_id = session.get('invitacion_id')
            inv_token = session.get('invitacion_token')
            if inv_id and inv_token:
                return redirect(url_for('pollas.invitacion', id=inv_id, token=inv_token))
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('principal.index')
            return redirect(next_page)
            
        flash('Credenciales incorrectas. Verifica tu correo y contraseña.', 'danger')
        
    return render_template('autenticacion/login.html')

@autenticacion_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('autenticacion.login'))

@autenticacion_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        correo = request.form.get('correo')
        nombre_usuario = request.form.get('nombre_usuario')
        password = request.form.get('password')
        
        usuario_existente = Usuario.query.filter(Usuario.correo == correo, Usuario.id != current_user.id).first()
        if usuario_existente:
            flash('Ese correo ya está siendo utilizado por otra persona.', 'danger')
            return redirect(url_for('autenticacion.perfil'))
            
        current_user.correo = correo
        current_user.nombre_usuario = nombre_usuario
        
        if password:
            current_user.contrasena_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            
        db.session.commit()
        flash('Tu identidad ha sido actualizada con éxito.', 'success')
        return redirect(url_for('autenticacion.perfil'))
        
    return render_template('autenticacion/perfil.html')
