from flask import jsonify
from common.bd import SessionLocal
from models.usuario import Usuario


def listar_usuarios(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    session = SessionLocal()

    try:
        usuarios = session.query(Usuario).all()

        data = [
            {
                "id": u.id,
                "nombre": u.nombre,
                "email": u.email,
                "rol": u.rol,
                "created_at": str(u.created_at)
            }
            for u in usuarios
        ]

        return jsonify({"ok": True, "data": data}), 200

    finally:
        session.close()