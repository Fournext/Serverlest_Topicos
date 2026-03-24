from flask import jsonify
from common.bd import SessionLocal
from models.nota_salida import NotaSalida

def obtener_nota_salida(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	nota_id = request.args.get("id")
	if not nota_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		nota = session.get(NotaSalida, int(nota_id))
		if not nota:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		return jsonify({
			"ok": True,
			"data": {
				"id": nota.id,
				"tipo_salida": nota.tipo_salida,
				"motivo": nota.motivo,
				"id_user": nota.id_user,
				"created_at": str(nota.created_at)
			}
		}), 200
	finally:
		session.close()