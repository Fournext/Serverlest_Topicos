from flask import jsonify
from common.bd import SessionLocal
from models.detalle_salida import DetalleSalida

def obtener_detalle_salida(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	detalle_id = request.args.get("id")
	if not detalle_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		detalle = session.get(DetalleSalida, int(detalle_id))
		if not detalle:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		return jsonify({
			"ok": True,
			"data": {
				"id": detalle.id,
				"cantidad_salida": detalle.cantidad_salida,
				"precio_unitario": float(detalle.precio_unitario),
				"ubicacion_salida": detalle.ubicacion_salida,
				"id_producto": detalle.id_producto,
				"id_nota_salida": detalle.id_nota_salida
			}
		}), 200
	finally:
		session.close()
