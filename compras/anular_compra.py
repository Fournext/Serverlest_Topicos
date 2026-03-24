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

        detalles = listar_detalles_por_compra(compra.id)
        for detalle in detalles:
            detalle_id = detalle.get("id")
            if detalle_id:
                anular_detalle_compra(detalle_id)

        return jsonify({"ok": True, "message": "Compra y detalles anulados correctamente", "data": {
            "id": compra.id,
            "usuario_id": compra.usuario_id,
            "total": float(compra.total),
            "estado": compra.estado
        }}), 200
    finally:
        session.close()
        
def listar_detalles_por_compra(compra_id):
    try:
        resp = requests.get(f"https://southamerica-east1-gen-lang-client-0878332190.cloudfunctions.net/compras/listar_detallecompra?compra_id={compra_id}")
        if resp.status_code == 200:
            return resp.json().get("data", [])
        return []
    except Exception:
        return []

def anular_detalle_compra(detalle_id):
    try:
        payload = {"id": detalle_id, "estado": "anulado"}
        requests.put("https://southamerica-east1-gen-lang-client-0878332190.cloudfunctions.net/compras/anular_detallecompra", json=payload)
    except Exception:
        pass        
