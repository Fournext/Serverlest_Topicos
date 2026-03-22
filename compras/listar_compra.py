from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests


def listar_compras(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        data = request.get_json(silent=True) or {}
        usuario_id = data.get("usuario_id")

    if not usuario_id:
        return jsonify({"ok": False, "message": "Falta usuario_id"}), 400

    session = SessionLocal()
    try:
        compras = session.query(Compra).filter(Compra.usuario_id == usuario_id, Compra.estado != "anulada").all()
        compras_list = [
            {
                "id": c.id,
                "usuario_id": c.usuario_id,
                "total": float(c.total),
                "estado": c.estado
            }
            for c in compras
        ]
        return jsonify({"ok": True, "data": compras_list}), 200
    finally:
        session.close()
