from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from datetime import date, datetime
from aplicacion.extensiones import db
from aplicacion.modelos import PreguntaTrivia, RespuestaTriviaUsuario

principal_bp = Blueprint('principal', __name__)

@principal_bp.route('/')
def index():
    trivia_hoy = PreguntaTrivia.query.filter_by(fecha_para_mostrar=date.today()).first()
    ya_respondio = False
    
    if current_user.is_authenticated and trivia_hoy:
        respuesta = RespuestaTriviaUsuario.query.filter_by(usuario_id=current_user.id, pregunta_id=trivia_hoy.id).first()
        if respuesta:
            ya_respondio = True

    return render_template('principal/index.html', trivia=trivia_hoy, ya_respondio=ya_respondio)

@principal_bp.route('/trivia/responder', methods=['POST'])
def responder_trivia():
    if not current_user.is_authenticated:
        flash("Debes estar conectado para responder la trivia.", "danger")
        return redirect(url_for('autenticacion.login'))

    pregunta_id = request.form.get('pregunta_id')
    opcion_elegida = request.form.get('opcion_elegida')
    
    if not pregunta_id or not opcion_elegida:
        flash("Respuesta no válida.", "danger")
        return redirect(url_for('principal.index'))

    pregunta = PreguntaTrivia.query.get_or_404(int(pregunta_id))
    
    # Verificar si ya respondió
    existe = RespuestaTriviaUsuario.query.filter_by(usuario_id=current_user.id, pregunta_id=pregunta.id).first()
    if existe:
        flash("Ya habías respondido la trivia de hoy.", "warning")
        return redirect(url_for('principal.index'))

    es_correcta = (pregunta.opcion_correcta.upper() == opcion_elegida.upper())
    
    # Otorgar puntos base (luego el ranking de cada polla multiplicará esto o lo leerá dinámicamente)
    puntos = 1 if es_correcta else 0
    
    nueva_respuesta = RespuestaTriviaUsuario(
        usuario_id=current_user.id,
        pregunta_id=pregunta.id,
        opcion_elegida=opcion_elegida.upper(),
        es_correcta=es_correcta,
        puntos_obtenidos=puntos,
        fecha_respuesta=datetime.utcnow()
    )
    db.session.add(nueva_respuesta)
    db.session.commit()
    
    if es_correcta:
        flash(f"¡Correcto! {pregunta.explicacion}", "success")
    else:
        flash(f"Incorrecto. La respuesta era la {pregunta.opcion_correcta}. {pregunta.explicacion}", "danger")
        
    return redirect(url_for('principal.index'))

@principal_bp.route('/ranking')
def ranking():
    return "Ranking (En construcción)"
