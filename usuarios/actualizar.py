from flask import jsonify
from common.bd import SessionLocal
from models.usuario import Usuario
from usuarios.utils import hash_password


def actualizar_usuario(request):
    if request.method != "PUT":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}
    user_id = data.get("id")

    if not user_id:
        return jsonify({"ok": False, "message": "ID requerido"}), 400

    session = SessionLocal()

    try:
        usuario = session.get(Usuario, int(user_id))

        if not usuario:
            return jsonify({"ok": False, "message": "No encontrado"}), 404

        if "nombre" in data:
            usuario.nombre = data["nombre"]

        if "email" in data:
            usuario.email = data["email"]

        if "password" in data:
            usuario.password = hash_password(data["password"])

        if "rol" in data:
            usuario.rol = data["rol"]

        session.commit()

        return jsonify({"ok": True, "message": "Actualizado"}), 200

    finally:
        session.close()