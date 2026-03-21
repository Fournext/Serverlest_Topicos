from flask import jsonify
from sqlalchemy.exc import IntegrityError
from common.bd import SessionLocal
from models.usuario import Usuario
from usuarios.utils import hash_password


def crear_usuario(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")
    rol = data.get("rol", "user")

    if not nombre or not email or not password:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    session = SessionLocal()

    try:
        usuario = Usuario(
            nombre=nombre,
            email=email,
            password=hash_password(password),
            rol=rol,
        )

        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        return jsonify({
            "ok": True,
            "data": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol
            }
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Email ya existe"}), 409

    finally:
        session.close()