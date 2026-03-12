from flask import Blueprint, jsonify, request
from app.db import get_connection, init_db

usuarios_bp = Blueprint("usuarios", __name__)

init_db()


@usuarios_bp.get("/")
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id,nombre,email,rol FROM usuarios")
    rows = cursor.fetchall()

    conn.close()

    usuarios = [dict(row) for row in rows]

    return jsonify({
        "total": len(usuarios),
        "usuarios": usuarios
    })


@usuarios_bp.get("/<int:usuario_id>")
def obtener_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id,nombre,email,rol FROM usuarios WHERE id=?", (usuario_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(dict(row))


@usuarios_bp.post("/")
def crear_usuario():
    data = request.get_json()

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")
    rol = data.get("rol", "user")

    if not nombre or not email or not password:
        return jsonify({"error": "nombre, email y password son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre,email,password,rol)
            VALUES (?,?,?,?)
        """, (nombre, email, password, rol))

        conn.commit()
        usuario_id = cursor.lastrowid

    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

    conn.close()

    return jsonify({
        "mensaje": "usuario creado",
        "id": usuario_id
    }), 201


@usuarios_bp.put("/<int:usuario_id>")
def actualizar_usuario(usuario_id):
    data = request.get_json()

    nombre = data.get("nombre")
    rol = data.get("rol")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre = nombre or usuario["nombre"]
    rol = rol or usuario["rol"]

    cursor.execute("""
        UPDATE usuarios
        SET nombre=?, rol=?
        WHERE id=?
    """, (nombre, rol, usuario_id))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "usuario actualizado"})


@usuarios_bp.delete("/<int:usuario_id>")
def eliminar_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    cursor.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "usuario eliminado"})