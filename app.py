import os
import traceback
import webbrowser
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server
from consultas import (
    total_consumos_hoy,
    total_consumos_semana,
    total_usuarios,
    total_eventos_auditoria,
    ultimos_consumos,
    registrar_consumo,
    user_exists,
    consumo_duplicado,
    registrar_usuario,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def render_template(template_name, context=None):
    context = context or {}
    template_path = os.path.join(BASE_DIR, "templates", template_name)
    if not os.path.exists(template_path):
        print(f"[TEMPLATE ERROR] Template no encontrado: {template_path}")
        try:
            print("[TEMPLATE ERROR] Templates disponibles:", os.listdir(os.path.join(BASE_DIR, "templates")))
        except Exception as list_error:
            print(f"[TEMPLATE ERROR] No se pudo listar templates: {list_error}")
        raise FileNotFoundError(f"Template no encontrado: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content.encode("utf-8")


def redirect(location):
    return [("Location", location)], b""


def try_db(func, *args, default=None, operation_description=None):
    try:
        return True, func(*args)
    except Exception as error:
        description = operation_description or func.__name__
        print(f"[DB ERROR] {description}: {error}")
        traceback.print_exc()
        return False, default


def parse_post_data(environ):
    try:
        request_body_size = int(environ.get("CONTENT_LENGTH", 0) or 0)
    except ValueError:
        request_body_size = 0
    request_body = environ["wsgi.input"].read(request_body_size).decode("utf-8")
    return {k: v[0] if v else "" for k, v in parse_qs(request_body).items()}


def build_flash_query(message, category="success"):
    return urlencode({"flash": message, "category": category})


def safe_page_response(start_response, page_func, *args, status="200 OK"):
    try:
        body = page_func(*args)
        start_response(status, [("Content-Type", "text/html; charset=utf-8")])
        return [body]
    except FileNotFoundError as error:
        print(f"[TEMPLATE ERROR] {error}")
        start_response("500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        return [error_page("Archivo de plantilla no encontrado.")]
    except Exception as error:
        print(f"[PAGE ERROR] {error}")
        traceback.print_exc()
        start_response("500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        return [error_page("Error interno al procesar la página.")]


def dashboard_page(flash_message="", flash_category="success"):
    db_errors = []
    ok, consumo_hoy = try_db(total_consumos_hoy, default=0, operation_description="total_consumos_hoy")
    if not ok:
        db_errors.append("no fue posible obtener el total de consumos de hoy")

    ok, consumo_semana = try_db(total_consumos_semana, default=0, operation_description="total_consumos_semana")
    if not ok:
        db_errors.append("no fue posible obtener el total de consumos de la semana")

    ok, usuarios_total = try_db(total_usuarios, default=0, operation_description="total_usuarios")
    if not ok:
        db_errors.append("no fue posible obtener el total de usuarios")

    ok, eventos_auditoria = try_db(total_eventos_auditoria, default=0, operation_description="total_eventos_auditoria")
    if not ok:
        db_errors.append("no fue posible obtener el total de eventos de auditoría")

    ok, consumos = try_db(ultimos_consumos, 8, default=[], operation_description="ultimos_consumos")
    if not ok:
        db_errors.append("no fue posible obtener los últimos consumos")

    rows = ""
    for consumo in consumos:
        rows += (
            "<tr>"
            f"<td>{consumo.get('id')}</td>"
            f"<td>{consumo.get('cedula_usuario')}</td>"
            f"<td>{consumo.get('nombre')}</td>"
            f"<td>{consumo.get('id_turno')}</td>"
            f"<td>{consumo.get('fecha')}</td>"
            f"<td>{consumo.get('hora')}</td>"
            "</tr>"
        )

    metrics = {
        "consumo_hoy": consumo_hoy,
        "consumo_semana": consumo_semana,
        "usuarios_total": usuarios_total,
        "eventos_auditoria": eventos_auditoria,
        "rows_consumo": rows or "<tr><td colspan='6'>No hay consumos registrados.</td></tr>",
    }

    if db_errors:
        if flash_message:
            flash_message = flash_message + " " + " / ".join(db_errors)
        else:
            flash_message = " / ".join(db_errors)
        flash_category = "warning"

    if flash_message:
        metrics["flash_block"] = (
            f"<div class=\"alert alert-{flash_category} alert-dismissible fade show\" role=\"alert\">"
            f"{flash_message}"
            "<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Cerrar\"></button>"
            "</div>"
        )
    else:
        metrics["flash_block"] = ""
    return render_template("dashboard.html", metrics)


def registro_page(flash_message="", flash_category="success"):
    metrics = {"flash_message": flash_message, "flash_category": flash_category}
    if flash_message:
        metrics["flash_block"] = (
            f"<div class=\"alert alert-{flash_category} alert-dismissible fade show\" role=\"alert\">"
            f"{flash_message}"
            "<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Cerrar\"></button>"
            "</div>"
        )
    else:
        metrics["flash_block"] = ""
    return render_template("registro.html", metrics)


def error_page(message):
    return (
        "<html><head><meta charset=\"utf-8\"><title>Error</title>"
        "<link href=\"/static/style.css\" rel=\"stylesheet\"></head><body>"
        "<div class=\"container py-5\">"
        "<h1 class=\"mb-4\">Error interno del servidor</h1>"
        f"<div class=\"alert alert-danger\">{message}</div>"
        "<a class=\"btn btn-primary\" href=\"/\">Volver al dashboard</a>"
        "</div></body></html>"
    ).encode("utf-8")


def application(environ, start_response):
    try:
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")

        if path.startswith("/static/"):
            static_path = os.path.join(BASE_DIR, path.lstrip("/"))
            if os.path.exists(static_path):
                content_type = "text/css" if static_path.endswith(".css") else "application/octet-stream"
                start_response("200 OK", [("Content-Type", content_type)])
                with open(static_path, "rb") as f:
                    return [f.read()]
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Archivo estatico no encontrado"]

        if path in ["/", "/admin"] and method == "GET":
            query = parse_qs(environ.get("QUERY_STRING", ""))
            flash_message = query.get("flash", [""])[0]
            flash_category = query.get("category", ["success"])[0]
            return safe_page_response(start_response, dashboard_page, flash_message, flash_category)

        if path == "/registrar" and method == "POST":
            form = parse_post_data(environ)
            cedula_usuario = form.get("cedula_usuario", "").strip()
            id_turno = form.get("id_turno", "").strip()
            fecha = form.get("fecha", "").strip()
            hora = form.get("hora", "").strip()

            if not cedula_usuario or not id_turno or not fecha or not hora:
                location = "/?" + build_flash_query("Debe completar todos los campos.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            ok, exists = try_db(user_exists, cedula_usuario, default=None, operation_description="user_exists")
            if not ok:
                location = "/?" + build_flash_query("Error en la base de datos. Intente nuevamente más tarde.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            if not exists:
                location = "/?" + build_flash_query("Usuario no encontrado.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            ok, duplicate = try_db(consumo_duplicado, cedula_usuario, fecha, hora, default=False, operation_description="consumo_duplicado")
            if not ok:
                location = "/?" + build_flash_query("Error en la base de datos. Intente nuevamente más tarde.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            if duplicate:
                location = "/?" + build_flash_query("Ya existe un consumo con la misma fecha y hora.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            ok, _ = try_db(registrar_consumo, cedula_usuario, id_turno, fecha, hora, default=None, operation_description="registrar_consumo")
            if not ok:
                location = "/?" + build_flash_query("No se pudo registrar el consumo. Intente más tarde.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            location = "/?" + build_flash_query("Consumo registrado con éxito.", "success")
            start_response("303 See Other", redirect(location))
            return [b""]

        if path == "/registro" and method == "GET":
            query = parse_qs(environ.get("QUERY_STRING", ""))
            flash_message = query.get("flash", [""])[0]
            flash_category = query.get("category", ["success"])[0]
            return safe_page_response(start_response, registro_page, flash_message, flash_category)

        if path == "/registro" and method == "POST":
            form = parse_post_data(environ)
            cedula = form.get("cedula", "").strip()
            nombre = form.get("nombre", "").strip()
            apellido = form.get("apellido", "").strip()
            correo = form.get("correo", "").strip()
            ciudad = form.get("ciudad", "").strip()
            estado = form.get("estado", "").strip()
            codigo_postal = form.get("codigo_postal", "").strip()

            if not all([cedula, nombre, apellido, correo, ciudad, estado, codigo_postal]):
                location = "/registro?" + build_flash_query("Debe completar todos los campos.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            ok, exists = try_db(user_exists, cedula, default=None, operation_description="user_exists")
            if not ok:
                location = "/registro?" + build_flash_query("Error en la base de datos. Intente nuevamente más tarde.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            if exists:
                location = "/registro?" + build_flash_query("La cédula ya está registrada.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            ok, _ = try_db(registrar_usuario, cedula, nombre, apellido, correo, ciudad, estado, codigo_postal, default=None, operation_description="registrar_usuario")
            if not ok:
                location = "/registro?" + build_flash_query("No se pudo registrar el usuario. Intente más tarde.", "danger")
                start_response("303 See Other", redirect(location))
                return [b""]

            location = "/?" + build_flash_query("Usuario registrado con éxito.", "success")
            start_response("303 See Other", redirect(location))
            return [b""]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Ruta no encontrada"]

    except Exception as error:
        print(f"Error interno del servidor: {error}")
        traceback.print_exc()
        start_response("500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        return [error_page(str(error))]


if __name__ == "__main__":
    port = int(os.environ.get("SGSC_PORT", 8000))
    url = f"http://localhost:{port}/"
    with make_server("0.0.0.0", port, application) as httpd:
        print(f"Servidor SGSC INCES iniciado en {url}")
        print("Presiona CTRL+C para detenerlo.")
        webbrowser.open(url)
        httpd.serve_forever()
