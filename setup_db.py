from conexion import get_connection

SQL_CREATE = [
    "CREATE TABLE IF NOT EXISTS usuarios ("
    "cedula VARCHAR(20) PRIMARY KEY,"
    "nombre VARCHAR(100) NOT NULL,"
    "apellido VARCHAR(100),"
    "correo VARCHAR(150),"
    "ciudad VARCHAR(100),"
    "estado VARCHAR(100),"
    "codigo_postal VARCHAR(20),"
    "creado_en TIMESTAMP DEFAULT NOW()"
    ");",
    "CREATE TABLE IF NOT EXISTS consumos ("
    "id SERIAL PRIMARY KEY,"
    "cedula_usuario VARCHAR(20) NOT NULL,"
    "id_turno VARCHAR(20) NOT NULL,"
    "fecha DATE NOT NULL,"
    "hora TIME NOT NULL,"
    "creado_en TIMESTAMP DEFAULT NOW(),"
    "FOREIGN KEY (cedula_usuario) REFERENCES usuarios (cedula)"
    ");",
    "CREATE TABLE IF NOT EXISTS auditoria ("
    "id SERIAL PRIMARY KEY,"
    "evento VARCHAR(255) NOT NULL,"
    "origen VARCHAR(100),"
    "creado_en TIMESTAMP DEFAULT NOW()"
    ");",
]

SAMPLE_INSERTS = [
    (
        "INSERT INTO usuarios (cedula, nombre, apellido, correo, ciudad, estado, codigo_postal) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (cedula) DO NOTHING;",
        ("12345678", "Ana", "Pérez", "ana.perez@inces.example", "Caracas", "Distrito Capital", "1010"),
    ),
    (
        "INSERT INTO usuarios (cedula, nombre, apellido, correo, ciudad, estado, codigo_postal) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (cedula) DO NOTHING;",
        ("87654321", "Juan", "Ramirez", "juan.ramirez@inces.example", "Valencia", "Carabobo", "2001"),
    ),
    (
        "INSERT INTO auditoria (evento, origen) VALUES (%s, %s);",
        ("Inicio de prueba de base de datos", "setup_db"),
    ),
    (
        "INSERT INTO consumos (cedula_usuario, id_turno, fecha, hora) "
        "VALUES (%s, %s, %s, %s);",
        ("12345678", "1", "2026-05-12", "08:30"),
    ),
    (
        "INSERT INTO consumos (cedula_usuario, id_turno, fecha, hora) "
        "VALUES (%s, %s, %s, %s);",
        ("87654321", "2", "2026-05-12", "12:15"),
    ),
]


def run_setup():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for statement in SQL_CREATE:
                cursor.execute(statement)
            for query, params in SAMPLE_INSERTS:
                cursor.execute(query, params)
        conn.commit()
        print("Tablas creadas correctamente y datos de ejemplo insertados.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        run_setup()
    except Exception as error:
        print("No se pudo inicializar la base de datos:", error)
        raise