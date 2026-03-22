from flask import jsonify
from models.proveedor import Proveedor
from common.bd import SessionLocal

def eliminar_proveedor(request):
	if request.method != "DELETE":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	proveedor_id = data.get("id")
	if not proveedor_id:
		return jsonify({"ok": False, "message": "Falta id del proveedor"}), 400

	session = SessionLocal()
	try:
		proveedor = session.query(Proveedor).filter_by(id=proveedor_id).first()
		if not proveedor:
			return jsonify({"ok": False, "message": "Proveedor no encontrado"}), 404
		session.delete(proveedor)
		session.commit()
		return jsonify({"ok": True, "message": "Proveedor eliminado", "data": {
			"id": proveedor.id,
			"nombre": proveedor.nombre,
			"contacto": proveedor.contacto,
			"created_at": str(proveedor.created_at)
		}}), 200
	finally:
		session.close()
