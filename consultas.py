from conexion import execute_query


def total_consumos_hoy():
    query = "SELECT COUNT(*) AS total FROM registro_consumo WHERE fecha_consumo = CURRENT_DATE;"
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def total_consumos_semana():
    query = (
        "SELECT COUNT(*) AS total FROM registro_consumo "
        "WHERE fecha_consumo >= CURRENT_DATE - INTERVAL '6 days' AND fecha_consumo <= CURRENT_DATE;"
    )
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def total_usuarios():
    query = "SELECT COUNT(*) AS total FROM usuarios;"
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def total_eventos_auditoria():
    query = "SELECT COUNT(*) AS total FROM log_auditoria_sistema;"
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def ultimos_consumos(limit=8):
    query = (
        "SELECT rc.id_consumo as id, rc.cedula_usuario, u.nombre, rc.id_turno, rc.fecha_consumo as fecha, rc.hora_registro as hora "
        "FROM registro_consumo rc "
        "LEFT JOIN usuarios u ON rc.cedula_usuario = u.cedula "
        "ORDER BY rc.fecha_consumo DESC, rc.hora_registro DESC "
        "LIMIT %s;"
    )
    return execute_query(query, (limit,), fetch_all=True) or []


def user_exists(cedula_usuario):
    query = "SELECT 1 FROM usuarios WHERE cedula = %s LIMIT 1;"
    result = execute_query(query, (cedula_usuario,), fetch_one=True)
    return bool(result)


def consumo_duplicado(cedula_usuario, fecha, hora):
    query = (
        "SELECT 1 FROM registro_consumo WHERE cedula_usuario = %s "
        "AND fecha_consumo = %s AND hora_registro = %s LIMIT 1;"
    )
    result = execute_query(query, (cedula_usuario, fecha, hora), fetch_one=True)
    return bool(result)


def registrar_consumo(cedula_usuario, id_turno, fecha, hora):
    query = (
        "INSERT INTO registro_consumo (cedula_usuario, id_turno, id_punto, fecha_consumo, hora_registro, cedula_operador) "
        "VALUES (%s, %s, NULL, %s, %s, %s);"
    )
    execute_query(query, (cedula_usuario, id_turno or None, fecha, hora, cedula_usuario), commit=True)


def registrar_usuario(cedula, nombre, apellido, correo, ciudad, estado, codigo_postal):
    query = (
        "INSERT INTO usuarios (cedula, nombre, apellido, correo, telefono, id_tipo_beneficiario, id_departamento, id_estatus, fecha_registro) "
        "VALUES (%s, %s, %s, %s, %s, NULL, NULL, NULL, NOW());"
    )
    # Usando NULL para campos faltantes
    execute_query(query, (cedula, nombre, apellido, correo, '0000000000'), commit=True)
