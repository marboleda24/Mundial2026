# POLLA MUNDIAL 2026

## INTRODUCCIÓN
Como amantes y apasionados del fútbol este año se celebra nuevamente el evento magno de este deporte y como es tradicional organizamos una polla para unir a los amigos entorno a este magno acontecimiento. Este año es muy especial, porque se hará en un formato mucho más amplio y sobre todo porque estará Colombia. Por lo tanto, queremos desarrollar una herramienta informática que nos permita gestionarla con plena autonomía de los participantes y mínima gestión de los administradores; ágil, fácil de usar, que se pueda utilizar tanto en móviles como computadores y con características de gobernanza comunitaria y transparencia.

## OBJETIVOS

### GENERAL
Documentar la planificación del desarrollo de software de una plataforma para gestionar pollas futboleras transparente, comunitaria y fácil de usar y administrar.

### ESPECÍFICOS
- Plasmar la idea del desarrollo de la plataforma futbolera de una manera muy detallada.
- Dejar descritas las condiciones, filosofía y parámetros para el desarrollo y la operación de la polla futbolera.

## CONDICIONES GENERALES
- Se desarrollará en Python.
- Debe ser responsive.
- Debe ser muy intuitiva.
- Debe ser basada en la transparencia y la confiabilidad.
- Interface de usuario lo más limpia posible.
- La transparencia se garantizará con la visibilidad completa y detallada de LOGS.
- La gobernanza se implementará por medio de una DAO.

## DESCRIPCIÓN DEL PROYECTO

**Filosofía del Proyecto:** La aplicación está centrada en la facilidad, transparencia, confiabilidad y democracia que deberían tener todas las herramientas que tienen como objetivo unir a las personas y convocarlas a participar en situaciones de iteración comunitaria.

La aplicación debe crear un entorno virtual (PLATAFORMA) en el que un usuario registrado pueda crear una o varias pollas (Quiniela o sistema de apuestas) y convocar a otros usuarios para que se unan y participen.

- Cada "polla" es un universo administrado por su creador, pero las reglas del juego pueden ser sometidas a consenso entre sus participantes.
- Cada usuario podrá crear una o varias pollas.
- La transparencia en el cálculo de puntos y la inmediatez en la actualización de resultados son pilares fundamentales del ecosistema.

Un usuario registrado podrá gestionar una o varias Pollas, lo cual le permitirá Crear, administrar y/o unirse a múltiples pollas.

**Consenso Democrático:** El Sistema proporcionará una herramienta de votación para definir reglas y condiciones de la POLLA (puntos por acierto exacto, ganador, goles, etc.).

**Automatización:** La aplicación será lo más automatizada posible, se debe construir de manera que la interacción humana sea mínima. Esto se logrará por medio de Consumo de API para resultados de partidos y cálculo automático de posiciones, Registro y autogestión de usuarios y administradores.

**Experiencia de Usuario (UX):** La plataforma debe ser 100% Responsive, debe verse bien en cualquier pantalla. 
- Ingreso masivo de marcadores para facilitar la participación.
- Diseño Responsivo y altamente intuitivo.
- Actualización en tiempo real de la tabla de posiciones, marcadores de partidos finalizados, activación y/o desactivación de funciones según las condiciones definidas en la POLLA.

## FUNCIONALIDADES DE LA PLATAFORMA

**Gestión de Usuarios y Roles:** Registro e inicio de sesión, actualización del Perfil de usuario.

### Roles:
1. **Super Admin:** Gestión global de la plataforma.
2. **Administrador de Polla:** Creador de una polla, gestiona invitaciones y configuración inicial.
3. **Participante:** Usuario que se registra en la plataforma, se puede unir o crear una polla y en este caso pasa a ser administrador de la POLLA creada; también podrá unirse a otras pollas y quedará automáticamente como participante de la POLLA creada. Cada usuario podrá ingresar marcadores de los partidos a los que pertenezca y votar en los consensos que monten las POLLAS a las que pertenezca o las que monte la PLATAFORMA.

## OPERACIÓN DE CADA POLLA

El administrador de cada Polla podrá realizar una convocatoria masiva o enviar enlaces independientes para que los usuarios se registren en la plataforma y se unan a su POLLA.

El administrador podrá definir si pone a consideración de su comunidad las condiciones con las que se jugará la POLLA o impondrá su estrategia si así lo considera.
- **Si decide poner las condiciones a consideración de sus usuarios:** Lanzará la iniciativa y dará un tiempo prudente para aprobar o desaprobar las normas; la idea es que cada condición debe ser votada por separado, pero se podrán votar masivamente o independientemente por cada opción y podrán ser unas favorables y otras desfavorables.
- El administrador de la polla activará la opción de crear los partidos; esto se hace invocando la API que se haya implementado para este fin.

*En caso de fallo de la API o método de conectividad se implementará la posibilidad de la Edición Manual: Esta Capacidad la debe activar el administrador global de la plataforma.*

## Lógica de las Pollas (The Core)

- **Creación:** Un usuario crea una polla y define las reglas iniciales o convoca a consenso.
- **Configuración de Reglas:**
  - Definición de parámetros puntuables (ej. Resultado exacto, Ganador, Diferencia de goles, Goles de un equipo); esto se hará automáticamente con una tabla predefinida que tendrá todas las condiciones posibles y su estado.
  - Asignación de valores de puntos a cada parámetro.
  - Se aplicarán cada vez que se dé por concluido cada partido y el torneo en general.
  - Este mecanismo debe actualizar la tabla de puntuaciones.
- **Predicciones (Marcadores):** Cada POLLA definirá los tiempos apropiados para deshabilitar el ingreso de marcadores y definición de posiciones finales.

## OPERACIÓN DE LOS USUARIOS

Cada usuario tendrá el listado de los partidos y deberá registrar los marcadores antes del tiempo de gracia establecido en la polla; lo podrá hacer de forma masiva o individual y podrá cambiarlos antes de que se cumpla el tiempo de gracia definido por la POLLA.

- **Cierre de Predicciones:** Bloqueo automático de ingreso de marcadores pronósticos globales según las políticas de la POLLA.

## CÁLCULO Y RANKING

- **Motor de Cálculo:** Proceso que se ejecuta al finalizar un partido (o en tiempo real) para asignar puntos a cada participante según las reglas de la POLLA; la tabla de posiciones de los participantes se actualizará al finalizar cada partido.

## REQUERIMIENTOS TÉCNICOS

### Stack Tecnológico (Confirmado)
- **Backend:** Python (Flask) - Stack actual del proyecto.
- **ORM:** SQLAlchemy.
- **Frontend:** HTML5 + Jinja2 Templates + CSS Responsivo (posible integración con Alpine.js para reactividad).
- **Base de Datos:** PostgreSQL (Producción) / SQLite (Desarrollo).
- **Gestión de Paquetes:** `pip` (requirements.txt).

### Base de Datos
- **Normalización:** Estructura totalmente normalizada (3NF).
- **Entidades Clave:** `usuarios`, `pollas`, `partidos`, `equipos`, `predicciones`, `reglas`, `votos_reglas`, `posiciones`.
- **Idioma de DB:** Tablas y columnas estrictamente en **ESPAÑOL** (ej. `users` -> `usuarios`, `predictions` -> `predicciones`).

### Idioma y Documentación
- **Código:** Variables, funciones, clases y comentarios en **ESPAÑOL**.
- **Documentación:** Todos los commits, PRs, y archivos MD en **ESPAÑOL**.

## REGLAS DE DESARROLLO (User Rules)
1. **No Code Yet:** No escribir código de aplicación hasta que la BD y la arquitectura estén aprobadas.
2. **Database First:** Diseño del esquema de BD completo y validado antes de la lógica.
