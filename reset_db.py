import os
import shutil
from app import app, db
from sync_matches import sync_matches

DB_FILE = 'polla_mundial.db'
INSTANCE_DIR = 'instance'

def reset_database():
    print("--- INICIANDO RESET TOTAL DE LA BASE DE DATOS ---")
    
    # 1. Eliminar archivo de DB si existe
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Eliminado: {DB_FILE}")
        except Exception as e:
            print(f"Error borrando {DB_FILE}: {e}")

    # 2. Eliminar carpeta instance si existe (Flask a veces guarda ahí la db)
    if os.path.exists(INSTANCE_DIR):
        try:
            shutil.rmtree(INSTANCE_DIR)
            print(f"Eliminado carpeta: {INSTANCE_DIR}")
        except Exception as e:
             print(f"Error borrando {INSTANCE_DIR}: {e}")

    # 3. Crear DB desde cero
    with app.app_context():
        try:
            db.create_all()
            print("Base de datos creada desde cero (tablas vacías).")
        except Exception as e:
             print(f"Error creando tablas: {e}")

    # 4. Sincronizar partidos
    print("Sincronizando partidos de nuevo...")
    try:
        sync_matches()
    except Exception as e:
        print(f"Error sincronizando partidos: {e}")

    print("--- RESET COMPLETADO ---")
    print("Por favor, inicia la app con 'python app.py' y crea un usuario nuevo.")

if __name__ == "__main__":
    reset_database()
