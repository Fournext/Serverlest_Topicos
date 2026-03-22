from flask import jsonify
from models.proveedor import Proveedor
from common.bd import SessionLocal

def listar_proveedor(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	session = SessionLocal()
	try:
		proveedores = session.query(Proveedor).all()
		proveedores_list = [
			{
				"id": p.id,
				"nombre": p.nombre,
				"contacto": p.contacto,
				"created_at": str(p.created_at)
			}
			for p in proveedores
		]
		return jsonify({"ok": True, "data": proveedores_list}), 200
	finally:
		session.close()
