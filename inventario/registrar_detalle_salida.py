from flask import jsonify
from common.bd import SessionLocal
from models.detalle_salida import DetalleSalida

def registrar_detalle_salida(request):
	if request.method != "POST":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	cantidad_salida = data.get("cantidad_salida")
	precio_unitario = data.get("precio_unitario")
	ubicacion_salida = data.get("ubicacion_salida")
	id_producto = data.get("id_producto")
	id_nota_salida = data.get("id_nota_salida")
	if not cantidad_salida or not precio_unitario or not id_producto or not id_nota_salida:
		return jsonify({"ok": False, "message": "Faltan campos requeridos"}), 400

	session = SessionLocal()
	try:
		detalle = DetalleSalida(
			cantidad_salida=cantidad_salida,
			precio_unitario=precio_unitario,
			ubicacion_salida=ubicacion_salida,
			id_producto=id_producto,
			id_nota_salida=id_nota_salida
		)
		session.add(detalle)
		session.commit()
		session.refresh(detalle)
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
		}), 201
	except Exception as e:
		session.rollback()
		return jsonify({"ok": False, "message": str(e)}), 500
	finally:
		session.close()
