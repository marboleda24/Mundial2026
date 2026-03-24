# POLLA MUNDIAL 2026

## Descripción del Proyecto
Plataforma web comunitaria, transparente y fácil de usar para la gestión de pollas futboleras. Desarrollada específicamente para el Mundial 2026 (y adaptable a otros torneos), permite a los usuarios crear, administrar y participar en múltiples pollas bajo un sistema de reglas basado en consenso y votación.

### Características Principales:
- **Gestión Multi-Polla:** Un usuario puede crear múltiples pollas o unirse a las de sus amigos.
- **Transparencia Total:** Trazabilidad asegurada mediante un Log de Auditoría para rastrear cálculos de puntos y cambios de reglas.
- **Sistema de Votación (DAO):** Reglas configurables que pueden ser impuestas por el administrador o sometidas a consenso democrático.
- **Autenticación Robusta:** Acceso por correo electrónico, contraseñas encriptadas fuertemente y modelos preparados para OAuth (Login con Google).
- **Diseño 100% en Español:** Código, variables, comentarios y base de datos nombrados nativamente en español.

---

## Detalle Técnico y Arquitectura
El proyecto fue construido bajo el paradigma **"Database First"**, garantizando un esquema robusto y normalizado (3NF) antes de codificar la lógica iterativa.

### Stack Tecnológico
- **Backend:** Python (Flask).
- **Base de Datos:** SQLite (Desarrollo) / PostgreSQL (Producción).
- **ORM:** Flask-SQLAlchemy.
- **Autenticación:** Flask-Login, Validator y Werkzeug Security.
- **Frontend:** HTML5, CSS Responsivo y plantillas Jinja2.

### Estructura de Directorios (Patrón Modular)
```text
/Mundial2026/
├── aplicacion/           # Módulo raíz de la aplicación (Application Factory)
│   ├── __init__.py      # Inicializador de la App, Config y Registro de Blueprints
│   ├── modelos.py       # Definición de Entidades SQLAlchemy (Usuarios, Pollas, etc.)
│   ├── extensiones.py   # Variables y configuraciones globales para prever ciclos de importación
│   ├── rutas/           # Blueprints divididos por dominio (autenticacion.py, principal.py)
│   ├── motor/           # Lógica central (Cálculo de puntos y rankings)
│   ├── plantillas/      # Archivos HTML y vistas
│   └── estaticos/       # CSS y JS de la UI
├── CONTEXTO_MUNDIAL2026.md # Reglas y Filosofía originarias del proyecto
├── iniciar.py           # Script punto de entrada principal
├── requirements.txt     # Dependencias del entorno
└── README.md            # Este archivo
```

---

## Guía de Instalación y Ejecución Local

Para desplegar este proyecto en tu entorno de desarrollo, sigue de cerca estos pasos:

### 1. Activar tu Entorno Virtual
Es altamente recomendable aislar tus librerías utilizando `venv`.
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar Requerimientos
Una vez activado, instala todas las librerías definidas en el proyecto:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el Servidor
La propia fábrica de la aplicación auto-chequea la existencia de la base de datos y levantará el esquema (`polla_mundial_v2.db`) la primera vez que se ejecute si no existe.
```bash
python iniciar.py
```

### 4. Accesibilidad
Una vez en consola veas `* Running on http://127.0.0.1:5000`, abre tu navegador en esa dirección y comienza a gestionar las inscripciones.
