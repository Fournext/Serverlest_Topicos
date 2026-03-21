from flask import jsonify
from common.bd import SessionLocal
from models.productos import Producto

def crear_producto(request):
	if request.method != "POST":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	nombre = data.get("nombre")
	descripcion = data.get("descripcion")
	stock_actual = data.get("stock_actual", 0)

	if not nombre or not descripcion:
		return jsonify({"ok": False, "message": "Faltan campos"}), 400

	session = SessionLocal()
	try:
		producto = Producto(
			nombre=nombre,
			descripcion=descripcion,
			stock_actual=stock_actual
		)
		session.add(producto)
		session.commit()
		session.refresh(producto)
		return jsonify({
			"ok": True,
			"data": {
				"id": producto.id,
				"nombre": producto.nombre,
				"descripcion": producto.descripcion,
				"stock_actual": producto.stock_actual,
				"created_at": str(producto.created_at)
			}
		}), 201
	except Exception as e:
		session.rollback()
		return jsonify({"ok": False, "message": str(e)}), 500
	finally:
		session.close()
