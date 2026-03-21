from flask import jsonify
from common.bd import SessionLocal
from models.usuario import Usuario


def eliminar_usuario(request):
    if request.method != "DELETE":
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

        session.delete(usuario)
        session.commit()

        return jsonify({"ok": True, "message": "Eliminado"}), 200

    finally:
        session.close()