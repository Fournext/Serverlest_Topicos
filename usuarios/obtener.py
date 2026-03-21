from flask import jsonify
from common.bd import SessionLocal
from models.usuario import Usuario


def obtener_usuario(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    user_id = request.args.get("id")

    if not user_id:
        return jsonify({"ok": False, "message": "ID requerido"}), 400

    session = SessionLocal()

    try:
        usuario = session.get(Usuario, int(user_id))

        if not usuario:
            return jsonify({"ok": False, "message": "No encontrado"}), 404

        return jsonify({
            "ok": True,
            "data": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol,
                "created_at": str(usuario.created_at)
            }
        }), 200

    finally:
        session.close()