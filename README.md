# SGSC INCES - Dashboard PostgreSQL

Proyecto simple en Python para conectar un dashboard HTML con PostgreSQL, sin frameworks complejos.

## Estructura del proyecto

- `app.py` - servidor HTTP y renderizado de la página principal
- `conexion.py` - configuración y manejo de la conexión PostgreSQL
- `consultas.py` - funciones SQL separadas para métricas y registros
- `templates/dashboard.html` - plantilla HTML del dashboard
- `static/style.css` - estilos modernos con azul claro y responsive
- `schema.sql` - SQL de inicialización de base de datos y datos de prueba

## Requisitos

- Python 3.10+ (o 3.8+)
- PostgreSQL
- `psycopg2`

## Instalación de dependencias

1. Crear un entorno virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Instalar `psycopg2`:

```powershell
pip install psycopg2-binary
```

## Configuración de PostgreSQL

1. Iniciar PostgreSQL localmente.
2. Crear la base de datos `sistema_comedor` (o usar el nombre configurado en `conexion.py`).
3. Crear las tablas e insertar datos de prueba con `schema.sql`:

```powershell
psql -U postgres -p 5433 -d sistema_comedor -f schema.sql
```

4. Si prefieres inicializar con Python, ejecuta:

```powershell
python setup_db.py
```

5. Ajustar credenciales en `conexion.py` o mediante variables de entorno:

- `SGSC_DB_HOST`
- `SGSC_DB_PORT`
- `SGSC_DB_USER`
- `SGSC_DB_PASSWORD`
- `SGSC_DB_NAME`
- `SGSC_PORT` (opcional, puerto del servidor)

## Ejecución

```powershell
python app.py
```

Acceder en el navegador:

```
http://localhost:8000
```

## Probar el dashboard

- Verás métricas dinámicas: consumos hoy, consumos semana, usuarios totales y eventos de auditoría.
- El formulario `Registrar Consumo` guarda un nuevo consumo en PostgreSQL.
- La tabla `Últimos Consumos` se genera desde la base de datos.
- El enlace `Registrar Usuario` lleva a un formulario para agregar nuevos usuarios al sistema.
- Los mensajes flash aparecen después de cada acción.

## Notas de validación

- Comprueba que no haya campos vacíos.
- El usuario debe existir en la tabla `usuarios`.
- No se permite consumir la misma fecha/hora para un mismo usuario.
