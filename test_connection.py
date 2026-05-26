from conexion import get_connection

try:
    conn = get_connection()
    print('OK', conn.dsn)
    conn.close()
except Exception as error:
    print('ERROR', error)
    raise