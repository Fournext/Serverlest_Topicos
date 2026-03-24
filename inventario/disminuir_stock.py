from flask import jsonify
from common.bd import SessionLocal
from models.productos import Producto

def disminuir_stock(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	producto_id = data.get("producto_id")
	cantidad = data.get("cantidad")
	if not producto_id or cantidad is None:
		return jsonify({"ok": False, "message": "ID y cantidad requeridos"}), 400

	session = SessionLocal()
	try:
		producto = session.get(Producto, int(producto_id))
		if not producto:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		if producto.stock_actual is None:
			producto.stock_actual = 0
		if producto.stock_actual < cantidad:
			return jsonify({"ok": False, "message": "Stock insuficiente"}), 400

		producto.stock_actual -= cantidad
		session.commit()
		return jsonify({"ok": True, "message": "Stock disminuido"}), 200
	finally:
		session.close()
