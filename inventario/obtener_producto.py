from flask import jsonify
from common.bd import SessionLocal
from models.productos import Producto
def obtener_producto(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	producto_id = request.args.get("id")
	if not producto_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		producto = session.get(Producto, int(producto_id))
		if not producto:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		return jsonify({
			"ok": True,
			"data": {
				"id": producto.id,
				"nombre": producto.nombre,
				"descripcion": producto.descripcion,
				"stock_actual": producto.stock_actual,
				"created_at": str(producto.created_at)
			}
		}), 200
	finally:
		session.close()
