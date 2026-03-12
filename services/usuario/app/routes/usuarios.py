from flask import Blueprint, jsonify, request
from psycopg.errors import UniqueViolation
from app.db import get_connection, init_db

from app.db import get_connection

usuarios_bp = Blueprint("usuarios", __name__)
init_db()

@usuarios_bp.get("/")
def listar_usuarios():
    query = """
        SELECT id, nombre, email, rol, created_at
        FROM usuarios
        ORDER BY id DESC
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            usuarios = cur.fetchall()

    return jsonify({
        "total": len(usuarios),
        "usuarios": usuarios
    }), 200


@usuarios_bp.get("/<int:usuario_id>")
def obtener_usuario(usuario_id):
    query = """
        SELECT id, nombre, email, rol, created_at
        FROM usuarios
        WHERE id = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (usuario_id,))
            usuario = cur.fetchone()

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuario), 200

# Crear Usuarios {nombre: , email: , password: , rol: }
@usuarios_bp.post("/")
def crear_usuario():
    data = request.get_json(silent=True) or {}

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    rol = (data.get("rol") or "user").strip()

    if not nombre or not email or not password:
        return jsonify({"error": "nombre, email y password son obligatorios"}), 400

    query = """
        INSERT INTO usuarios (nombre, email, password, rol)
        VALUES (%s, %s, %s, %s)
        RETURNING id, nombre, email, rol, created_at
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (nombre, email, password, rol))
                usuario = cur.fetchone()
            conn.commit()
    except UniqueViolation:
        return jsonify({"error": "El email ya existe"}), 400

    return jsonify({
        "mensaje": "Usuario creado correctamente",
        "usuario": usuario
    }), 201


# Editar Usuarios {nombre: , email: , password: , rol: }
@usuarios_bp.put("/<int:usuario_id>")
def actualizar_usuario(usuario_id):
    data = request.get_json(silent=True) or {}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nombre, email, password, rol, created_at
                FROM usuarios
                WHERE id = %s
                """,
                (usuario_id,)
            )
            usuario_actual = cur.fetchone()

            if not usuario_actual:
                return jsonify({"error": "Usuario no encontrado"}), 404

            nombre = (data.get("nombre") or usuario_actual["nombre"]).strip()
            email = (data.get("email") or usuario_actual["email"]).strip().lower()
            password = (data.get("password") or usuario_actual["password"]).strip()
            rol = (data.get("rol") or usuario_actual["rol"]).strip()

            try:
                cur.execute(
                    """
                    UPDATE usuarios
                    SET nombre = %s,
                        email = %s,
                        password = %s,
                        rol = %s
                    WHERE id = %s
                    RETURNING id, nombre, email, rol, created_at
                    """,
                    (nombre, email, password, rol, usuario_id)
                )
                usuario_actualizado = cur.fetchone()
                conn.commit()
            except UniqueViolation:
                conn.rollback()
                return jsonify({"error": "El email ya existe"}), 400

    return jsonify({
        "mensaje": "Usuario actualizado correctamente",
        "usuario": usuario_actualizado
    }), 200


@usuarios_bp.delete("/<int:usuario_id>")
def eliminar_usuario(usuario_id):
    query = """
        DELETE FROM usuarios
        WHERE id = %s
        RETURNING id
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (usuario_id,))
            eliminado = cur.fetchone()
        conn.commit()

    if not eliminado:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "mensaje": "Usuario eliminado correctamente",
        "id": eliminado["id"]
    }), 200