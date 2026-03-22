from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models import compra
from models.proveedor import Proveedor
from common.bd import SessionLocal
import requests


def crear_proveedor(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    nombre = data.get("nombre")
    contacto = data.get("contacto")

    if not nombre:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    session = SessionLocal()

    try:
        proveedor = Proveedor(
            nombre=nombre,
            contacto=contacto
        )

        session.add(proveedor)
        session.commit()
        session.refresh(proveedor)

        return jsonify({
            "ok": True,
            "data": {
                "id": proveedor.id,
                "nombre": proveedor.nombre,
                "contacto": proveedor.contacto
            }
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400

    finally:
        session.close()        
