from flask import jsonify
from common.bd import SessionLocal
from models.productos import Producto

def actualizar_producto(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	producto_id = data.get("id")
	if not producto_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		producto = session.get(Producto, int(producto_id))
		if not producto:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		if "nombre" in data:
			producto.nombre = data["nombre"]
		if "descripcion" in data:
			producto.descripcion = data["descripcion"]
		if "stock_actual" in data:
			producto.stock_actual = data["stock_actual"]

		session.commit()
		return jsonify({"ok": True, "message": "Actualizado"}), 200
	finally:
		session.close()
