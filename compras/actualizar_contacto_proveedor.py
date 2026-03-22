from flask import jsonify
from models.proveedor import Proveedor
from common.bd import SessionLocal

def actualizar_contacto_proveedor(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	proveedor_id = data.get("id")
	nuevo_contacto = data.get("contacto")
	if not proveedor_id or nuevo_contacto is None:
		return jsonify({"ok": False, "message": "Faltan campos: id y contacto"}), 400

	session = SessionLocal()
	try:
		proveedor = session.query(Proveedor).filter_by(id=proveedor_id).first()
		if not proveedor:
			return jsonify({"ok": False, "message": "Proveedor no encontrado"}), 404
		proveedor.contacto = nuevo_contacto
		session.commit()
		return jsonify({"ok": True, "message": "Contacto actualizado", "data": {
			"id": proveedor.id,
			"nombre": proveedor.nombre,
			"contacto": proveedor.contacto,
			"created_at": str(proveedor.created_at)
		}}), 200
	finally:
		session.close()
