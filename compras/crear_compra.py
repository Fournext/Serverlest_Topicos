from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests

URLUser = "/compras/crear"

def crear_compra(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    usuario_id = data.get("usuario_id")
    total = data.get("total")
    estado = data.get("estado", "pendiente")


    if not usuario_id or total is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    if not verificar_usuario(usuario_id):
        return jsonify({"ok": False, "message": "El usuario no existe"}), 404

    session = SessionLocal()

    try:
        compra = Compra(
            usuario_id=usuario_id,
            total=total,
            estado=estado
        )

        session.add(compra)
        session.commit()
        session.refresh(compra)

        return jsonify({
            "ok": True,
            "data": {
                "id": compra.id,
                "usuario_id": compra.usuario_id,
                "total": float(compra.total),
                "estado": compra.estado
            }
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400

    finally:
        session.close()

def verificar_usuario(usuario_id):
    try:
        response = requests.get(f"http://localhost:5000/usuarios/{usuario_id}")
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False