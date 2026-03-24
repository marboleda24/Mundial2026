from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from aplicacion.extensiones import db
from aplicacion.modelos import Partido, Prediccion, Polla, Torneo, ParticipantePolla, Equipo
from datetime import datetime, timezone

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
    
    # Traer todos los equipos en caché rápida
    equipos_dict = {e.id: e for e in Equipo.query.all()}
    
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('pred_local_'):
                partido_id = int(key.split('_')[2])
                goles_local = value
                goles_visitante = request.form.get(f'pred_visitante_{partido_id}')
                
                # Validar inputs
                if goles_local and goles_visitante and goles_local.isdigit() and goles_visitante.isdigit():
                    partido = Partido.query.get(partido_id)
                    
                    # Validar si aún se permite pronosticar
                    if partido and (partido.estado in ['NS', 'No Iniciado']) and partido.fecha_hora > datetime.now(timezone.utc).replace(tzinfo=None):
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
                        pred.fecha_prediccion = datetime.now(timezone.utc).replace(tzinfo=None)
                        pred.comentarios = "Pronóstico ingresado OK"
        
        db.session.commit()
        flash("Tus pronósticos futboleros han sido guardados exitosamente.", "success")
        return redirect(url_for('predicciones.ingresar', polla_id=polla_id))
        
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    return render_template('predicciones/ingresar.html', polla=polla, partidos=partidos, pred_dict=pred_dict, equipos_dict=equipos_dict, ahora=ahora)
