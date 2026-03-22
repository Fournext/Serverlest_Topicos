from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests


def anular_compra(request):
    if request.method != "PUT":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    usuario_id = data.get("usuario_id")
    total = data.get("total")
    estado = data.get("estado", "pendiente")
    compra_id = data.get("id")

    if not usuario_id or (total is None and not compra_id):
        return jsonify({"ok": False, "message": "Faltan campos: usuario_id y (total o id)"}), 400


    session = SessionLocal()
    try:
        if compra_id:
            compra = session.query(Compra).filter_by(id=compra_id, usuario_id=usuario_id).first()
        else:
            compra = session.query(Compra).filter_by(usuario_id=usuario_id, total=total, estado=estado).first()

        if not compra:
            return jsonify({"ok": False, "message": "Compra no encontrada"}), 404

        compra.estado = "anulada"
        session.commit()

        return jsonify({"ok": True, "message": "Compra anulada correctamente", "data": {
            "id": compra.id,
            "usuario_id": compra.usuario_id,
            "total": float(compra.total),
            "estado": compra.estado
        }}), 200
    finally:
        session.close()
