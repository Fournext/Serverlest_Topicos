from flask import jsonify
from common.bd import SessionLocal
from models.nota_salida import NotaSalida

def actualizar_nota_salida(request):
	if request.method != "PUT":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	nota_id = data.get("id")
	if not nota_id:
		return jsonify({"ok": False, "message": "ID requerido"}), 400

	session = SessionLocal()
	try:
		nota = session.get(NotaSalida, int(nota_id))
		if not nota:
			return jsonify({"ok": False, "message": "No encontrado"}), 404

		if "tipo_salida" in data:
			nota.tipo_salida = data["tipo_salida"]
		if "motivo" in data:
			nota.motivo = data["motivo"]
		if "id_user" in data:
			nota.id_user = data["id_user"]

		session.commit()
		return jsonify({"ok": True, "message": "Nota de salida actualizada"}), 200
	finally:
		session.close()
