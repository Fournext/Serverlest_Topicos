from flask import jsonify
from common.bd import SessionLocal
from models.productos import Producto

def listar_productos(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	session = SessionLocal()
	try:
		productos = session.query(Producto).all()
		data = [
			{
				"id": p.id,
				"nombre": p.nombre,
				"descripcion": p.descripcion,
				"stock_actual": p.stock_actual,
				"created_at": str(p.created_at)
			}
			for p in productos
		]
		return jsonify({"ok": True, "data": data}), 200
	finally:
		session.close()
