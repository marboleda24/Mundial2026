from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import Partido, Prediccion, Polla, Torneo, ParticipantePolla, Equipo
from datetime import datetime, timezone
from collections import defaultdict

predicciones_bp = Blueprint('predicciones', __name__, url_prefix='/predicciones')

@predicciones_bp.route('/polla/<int:polla_id>', methods=['GET', 'POST'])
@login_required
def ingresar(polla_id):
    polla = Polla.query.get_or_404(polla_id)
    participante = ParticipantePolla.query.filter_by(usuario_id=current_user.id, polla_id=polla_id).first()
    
    if not participante:
        flash("Debes unirte a la polla para poder enviar pronósticos.", "danger")
        return redirect(url_for('pollas.detalle', id=polla_id))
        
    partidos = Partido.query.filter_by(torneo_id=polla.torneo_id).order_by(Partido.fecha_hora.asc()).all()
    mis_predicciones = Prediccion.query.filter_by(usuario_id=current_user.id, polla_id=polla_id).all()
    pred_dict = {p.partido_id: p for p in mis_predicciones}
    
    # Agrupar partidos por jornada
    jornadas = defaultdict(list)
    for partido in partidos:
        jornada = partido.jornada or "Sin Jornada"
        jornadas[jornada].append(partido)
    
    # Traer todos los equipos en caché rápida
    equipos_dict = {e.id: e for e in Equipo.query.all()}
    
    # 1. Encontrar el partido inaugural para el Deadline de Torneo (Podio/Goleador)
    partido_inaugural = Partido.query.filter_by(torneo_id=polla.torneo_id).order_by(Partido.fecha_hora.asc()).first()
    deadline_torneo = None
    if partido_inaugural:
        from datetime import timedelta
        deadline_torneo = partido_inaugural.fecha_hora - timedelta(minutes=15)
    
    ahora = datetime.utcnow()
    
    if request.method == 'POST':
        # Bloque A: Predicciones de Favoritos (Sellar 15 min antes del primer partido)
        if deadline_torneo and ahora < deadline_torneo:
            campeon = request.form.get('campeon_pred')
            subcampeon = request.form.get('subcampeon_pred')
            tercer_puesto = request.form.get('tercer_puesto_pred')
            goleador = request.form.get('goleador_pred')
            
            if campeon and campeon.isdigit():
                participante.campeon_pred = int(campeon)
            if subcampeon and subcampeon.isdigit():
                participante.subcampeon_pred = int(subcampeon)
            if tercer_puesto and tercer_puesto.isdigit():
                participante.tercer_puesto_pred = int(tercer_puesto)
            if goleador and goleador.isdigit():
                participante.goleador_pred = int(goleador)
        else:
            flash("El tiempo para sellar tus favoritos (Podio/Goleador) ha expirado (15 min antes del mundial).", "warning")

        # Bloque B: Predicciones de Marcadores
        for key, value in request.form.items():
            if key.startswith('pred_local_'):
                partido_id = int(key.split('_')[2])
                goles_local = value
                goles_visitante = request.form.get(f'pred_visitante_{partido_id}')
                
                if goles_local and goles_visitante and goles_local.isdigit() and goles_visitante.isdigit():
                    partido = Partido.query.get(partido_id)
                    
                    # Validar Deadline de 15 minutos por partido
                    from datetime import timedelta
                    deadline_partido = partido.fecha_hora - timedelta(minutes=15)
                    
                    if partido and ahora < deadline_partido:
                        pred = pred_dict.get(partido_id)
                        if not pred:
                            pred = Prediccion(
                                usuario_id=current_user.id,
                                polla_id=polla_id,
                                partido_id=partido_id
                            )
                            db.session.add(pred)
                        
                        pred.goles_local_pred = int(goles_local)
                        pred.goles_visitante_pred = int(goles_visitante)
                        pred.fecha_prediccion = ahora
                        pred.comentarios = "Sincronizado"
                    else:
                        # Omitimos silenciosamente o avisamos si se intentó hackear el front
                        pass
        
        db.session.commit()
        flash("Tus pronósticos futboleros han sido procesados. ¡Mucha suerte!", "success")
        return redirect(url_for('predicciones.ingresar', polla_id=polla_id))
        
    # Preparar candidatos a goleador para el template
    from aplicacion.modelos import CandidatoGoleador
    candidatos_goleador = CandidatoGoleador.query.filter_by(torneo_id=polla.torneo_id).all()
    
    return render_template('predicciones/ingresar.html', 
                          polla=polla, 
                          jornadas=jornadas, 
                          pred_dict=pred_dict, 
                          equipos_dict=equipos_dict, 
                          ahora=ahora, 
                          participante=participante,
                          deadline_torneo=deadline_torneo,
                          candidatos_goleador=candidatos_goleador)
