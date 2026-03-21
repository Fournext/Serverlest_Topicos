from flask import jsonify
from common.bd import SessionLocal
from models.detalle_salida import DetalleSalida

def actualizar_detalle_salida(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	detalle_id = data.get("id")
	if not detalle_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		detalle = session.get(DetalleSalida, int(detalle_id))
		if not detalle:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		if "cantidad_salida" in data:
			detalle.cantidad_salida = data["cantidad_salida"]
		if "precio_unitario" in data:
			detalle.precio_unitario = data["precio_unitario"]
		if "ubicacion_salida" in data:
			detalle.ubicacion_salida = data["ubicacion_salida"]
		if "id_producto" in data:
			detalle.id_producto = data["id_producto"]
		if "id_nota_salida" in data:
			detalle.id_nota_salida = data["id_nota_salida"]

		session.commit()
		return jsonify({"ok": True, "message": "Detalle de salida actualizado"}), 200
	finally:
		session.close()
