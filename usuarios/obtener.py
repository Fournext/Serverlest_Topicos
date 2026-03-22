from flask import jsonify
from common.bd import SessionLocal
from models.usuario import Usuario


from flask import jsonify

def obtener_usuario(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    try:
        user_id = request.args.get("id")
        if not user_id:
            path_parts = request.path.rstrip("/").split("/")
            user_id = path_parts[-1]

        if not user_id.isdigit():
            return jsonify({"ok": False, "message": "ID inválido"}), 400

        user_id = int(user_id)

        session = SessionLocal()

        usuario = session.get(Usuario, user_id)

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

    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500

    finally:
        session.close()