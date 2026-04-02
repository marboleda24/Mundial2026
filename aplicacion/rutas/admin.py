from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import ConfiguracionGlobal, CandidatoGoleador, Torneo

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_superadmin():
    if not current_user.es_superadmin:
        flash("Acceso denegado. Se requieren privilegios de Super Administrador.", "danger")
        return redirect(url_for('principal.index'))

@admin_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    # Obtener configuración actual
    llm_proveedor = ConfiguracionGlobal.query.filter_by(clave='LLM_PROVEEDOR').first()
    llm_api_key = ConfiguracionGlobal.query.filter_by(clave='LLM_API_KEY').first()

    if request.method == 'POST':
        proveedor_nuevo = request.form.get('llm_proveedor')
        api_key_nueva = request.form.get('llm_api_key')

        if not llm_proveedor:
            llm_proveedor = ConfiguracionGlobal(clave='LLM_PROVEEDOR', descripcion='Proveedor de IA para la Trivia Diaria')
            db.session.add(llm_proveedor)
        
        if not llm_api_key:
            llm_api_key = ConfiguracionGlobal(clave='LLM_API_KEY', descripcion='Token secreto de acceso a la API')
            db.session.add(llm_api_key)

        llm_proveedor.valor = proveedor_nuevo
        llm_api_key.valor = api_key_nueva
        db.session.commit()

        flash("Configuraciones del bot de Trivia IA guardadas exitosamente.", "success")
        return redirect(url_for('admin.dashboard'))

    candidatos = CandidatoGoleador.query.all()
    torneos = Torneo.query.all()

    return render_template('admin/dashboard.html', proveedor=llm_proveedor.valor if llm_proveedor else '', api_key=llm_api_key.valor if llm_api_key else '', candidatos=candidatos, torneos=torneos)

@admin_bp.route('/goleador/agregar', methods=['POST'])
def agregar_goleador():
    nombre = request.form.get('nombre')
    torneo_id = request.form.get('torneo_id')
    
    if nombre and torneo_id:
        nuevo_candidato = CandidatoGoleador(nombre=nombre, torneo_id=torneo_id)
        db.session.add(nuevo_candidato)
        db.session.commit()
        flash(f"Agregado {nombre} a la terna de goleadores posibles.", "success")
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/goleador/eliminar/<int:id>', methods=['POST'])
def eliminar_goleador(id):
    candidato = CandidatoGoleador.query.get_or_404(id)
    db.session.delete(candidato)
    db.session.commit()
    flash(f"{candidato.nombre} fue removido de las opciones.", "info")
    return redirect(url_for('admin.dashboard'))

