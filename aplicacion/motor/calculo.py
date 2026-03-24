from aplicacion.extensiones import db
from aplicacion.modelos import Partido, Prediccion, Polla, ConfiguracionReglaPolla, PuntosPartido, PosicionesPolla, LogAuditoria
from datetime import datetime
from sqlalchemy import func

def procesar_partido(partido_id, user_admin_id=None):
    """
    Función core que toma un partido ya finalizado (con goles reales)
    y cruza estos datos con las predicciones de los usuarios,
    otorgando los puntos según las reglas de cada Polla.
    """
    partido = db.session.get(Partido, partido_id)
    if not partido or partido.estado not in ['FT', 'Finalizado', 'Finished']:
        return False, "El partido no existe o aún no ha finalizado."
        
    goles_l = partido.goles_local_real
    goles_v = partido.goles_visitante_real
    
    if goles_l is None or goles_v is None:
        return False, "Faltan los marcadores reales del partido."

    predicciones = Prediccion.query.filter_by(partido_id=partido_id).all()
    pollas_reglas = {}
    registros_guardados = 0
    
    for pred in predicciones:
        polla_id = pred.polla_id
        
        if polla_id not in pollas_reglas:
            reglas = ConfiguracionReglaPolla.query.filter_by(polla_id=polla_id, estado='Aprobada').all()
            pollas_reglas[polla_id] = {r.tipo_regla: r for r in reglas}
            
        reglas_polla = pollas_reglas[polla_id]
        
        # Evaluaciones booleanas
        acierto_exacto = (pred.goles_local_pred == goles_l) and (pred.goles_visitante_pred == goles_v)
        
        real_gana_local = goles_l > goles_v
        real_empate = goles_l == goles_v
        real_gana_visit = goles_l < goles_v
        
        pred_gana_local = pred.goles_local_pred > pred.goles_visitante_pred
        pred_empate = pred.goles_local_pred == pred.goles_visitante_pred
        pred_gana_visit = pred.goles_local_pred < pred.goles_visitante_pred
        
        acierto_ganador = (real_gana_local and pred_gana_local) or (real_empate and pred_empate) or (real_gana_visit and pred_gana_visit)
        
        puntos_totales = 0
        desglose = []
        regla_aplicada_id = None
        
        # Aplicamos la mejor regla (Exacto mata a Ganador usualmente)
        if acierto_exacto and "Acierto Exacto" in reglas_polla:
            regla_ex = reglas_polla["Acierto Exacto"]
            puntos_totales += regla_ex.puntos_asignados
            regla_aplicada_id = regla_ex.id
            desglose.append(f"Pleno al marcador (+{regla_ex.puntos_asignados})")
            
        elif acierto_ganador and "Acierto Ganador" in reglas_polla:
            regla_gan = reglas_polla["Acierto Ganador"]
            puntos_totales += regla_gan.puntos_asignados
            regla_aplicada_id = regla_gan.id
            desglose.append(f"Acierto al ganador (+{regla_gan.puntos_asignados})")
            
        if puntos_totales > 0 and regla_aplicada_id:
            # Control Anti-Duplicados
            existe = PuntosPartido.query.filter_by(usuario_id=pred.usuario_id, polla_id=polla_id, partido_id=partido_id).first()
            if not existe:
                nuevo_puntaje = PuntosPartido(
                    usuario_id=pred.usuario_id,
                    polla_id=polla_id,
                    partido_id=partido_id,
                    regla_aplicada_id=regla_aplicada_id,
                    puntos_sumados=puntos_totales,
                    comentarios=" | ".join(desglose)
                )
                db.session.add(nuevo_puntaje)
                registros_guardados += 1
                
    db.session.commit()
    
    # Recalcular Ranking Global para las pollas tocadas
    for polla_id in pollas_reglas.keys():
        recalcular_posiciones(polla_id)
        
    # LOG DE AUDITORÍA (Transparencia Total)
    log = LogAuditoria(
        usuario_id=user_admin_id,
        accion="Cálculo Automático de Puntos",
        entidad_afectada=f"Partido {partido_id}",
        detalle_json=f"Se evaluaron {len(predicciones)} predicciones. Se otorgaron puntos a {registros_guardados} aciertos.",
        direccion_ip="127.0.0.1 (Motor Backend)",
        comentarios="Motor de cálculo exitoso."
    )
    db.session.add(log)
    db.session.commit()
        
    return True, f"Procesado. Puntos otorgados a {registros_guardados} aciertos."

def recalcular_posiciones(polla_id):
    """
    Suma todos los PuntosPartido de un usuario en su Polla y actualiza su Posicion en la tabla final.
    """
    resultados = db.session.query(
        PuntosPartido.usuario_id, 
        func.sum(PuntosPartido.puntos_sumados).label('total')
    ).filter_by(polla_id=polla_id).group_by(PuntosPartido.usuario_id).order_by(func.sum(PuntosPartido.puntos_sumados).desc()).all()
    
    rank = 1
    for r in resultados:
        posicion = PosicionesPolla.query.filter_by(polla_id=polla_id, usuario_id=r.usuario_id).first()
        if not posicion:
            posicion = PosicionesPolla(polla_id=polla_id, usuario_id=r.usuario_id)
            db.session.add(posicion)
            
        posicion.puntos_totales = r.total
        posicion.posicion_ranking = rank
        rank += 1
        
    db.session.commit()
