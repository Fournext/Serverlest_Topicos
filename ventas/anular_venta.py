from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
import requests

def anular_venta(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}

	usuario_id = data.get("usuario_id")
	total = data.get("total")
	estado = data.get("estado", "pendiente")
	venta_id = data.get("id")

	if not usuario_id or (total is None and not venta_id):
		return jsonify({"ok": False, "message": "Faltan campos: usuario_id y (total o id)"}), 400

	session = SessionLocal()
	try:
		if venta_id:
			venta = session.query(Venta).filter_by(id=venta_id, usario_id=usuario_id).first()
		else:
			venta = session.query(Venta).filter_by(usario_id=usuario_id, total=total, estado=estado).first()

		if not venta:
			return jsonify({"ok": False, "message": "Venta no encontrada"}), 404

		venta.estado = "anulada"
		session.commit()

		detalles = listar_detalles_por_venta(venta.id)
		for detalle in detalles:
			detalle_id = detalle.get("id")
			if detalle_id:
				anular_detalle_venta(detalle_id)

		return jsonify({"ok": True, "message": "Venta y detalles anulados correctamente", "data": {
			"id": venta.id,
			"usuario_id": venta.usario_id,
			"total": float(venta.total),
			"estado": venta.estado
		}}), 200
	finally:
		session.close()

def listar_detalles_por_venta(venta_id):
	try:
		resp = requests.get(f"/detalle_venta/listar?venta_id={venta_id}")
		if resp.status_code == 200:
			return resp.json().get("data", [])
		return []
	except Exception:
		return []

def anular_detalle_venta(detalle_id):
	try:
		payload = {"id": detalle_id, "estado": "anulado"}
		requests.put(f"/detalle_venta/anular", json=payload)
	except Exception:
		pass
