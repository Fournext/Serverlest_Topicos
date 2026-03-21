from flask import jsonify
from common.bd import SessionLocal
from models.detalle_salida import DetalleSalida

def obtener_detalles_de_nota_salida(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	id_nota_salida = request.args.get("id_nota_salida")
	if not id_nota_salida:
		return jsonify({"ok": False, "message": "id_nota_salida requerido"}), 400

	session = SessionLocal()
	try:
		detalles = session.query(DetalleSalida).filter_by(id_nota_salida=int(id_nota_salida)).all()
		data = [
			{
				"id": d.id,
				"cantidad_salida": d.cantidad_salida,
				"precio_unitario": float(d.precio_unitario),
				"ubicacion_salida": d.ubicacion_salida,
				"id_producto": d.id_producto,
				"id_nota_salida": d.id_nota_salida
			}
			for d in detalles
		]
		return jsonify({"ok": True, "data": data}), 200
	finally:
		session.close()
