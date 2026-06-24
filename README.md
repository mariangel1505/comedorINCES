# SGSC INCES — Resumen rápido

Pequeña aplicación en Python que sirve un dashboard HTML conectado a PostgreSQL.

Requisitos mínimos
- Python 3.8+
- PostgreSQL
- Dependencia: `psycopg2-binary` (ver `requirements.txt`)

Variables de entorno (opcionales)
- `SGSC_DB_HOST` (por defecto: localhost)
- `SGSC_DB_PORT` (por defecto: 5433)
- `SGSC_DB_USER` (por defecto: postgres)
- `SGSC_DB_PASSWORD` (por defecto: 12345)
- `SGSC_DB_NAME` (por defecto: sistema_comedor)
- `SGSC_PORT` (puerto HTTP, por defecto: 8000)

Instalación y puesta en marcha
1. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Inicializar la base de datos (opcional):

```powershell
psql -U postgres -p 5433 -d sistema_comedor -f schema.sql
# o
python setup_db.py
```

4. Ejecutar la aplicación:

```powershell
python app.py
```

Accede en el navegador: http://localhost:8000

Archivos principales
- `app.py`: servidor WSGI y lógica HTTP
- `conexion.py`: conexión y helper para consultas a PostgreSQL
- `consultas.py`: funciones SQL reutilizables
- `setup_db.py` / `schema.sql`: creación de tablas y datos de ejemplo
- `templates/` y `static/`: frontend (Bootstrap desde CDN)

Soporte y pruebas
- Probar conexión: `python test_connection.py`
- Para producción considere usar un servidor WSGI robusto (Gunicorn/uvicorn) y configurar credenciales seguras.

Si quieres, genero un `requirements.txt` con versiones fijadas y un breve `deploy.md`.
