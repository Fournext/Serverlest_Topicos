from flask import jsonify
from common.bd import SessionLocal
from models.nota_salida import NotaSalida

def registrar_nota_salida(request):
	if request.method != "POST":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}
	tipo_salida = data.get("tipo_salida")
	motivo = data.get("motivo")
	id_user = data.get("id_user")
	if not tipo_salida or not id_user:
		return jsonify({"ok": False, "message": "tipo_salida e id_user requeridos"}), 400

	session = SessionLocal()
	try:
		nota = NotaSalida(
			tipo_salida=tipo_salida,
			motivo=motivo,
			id_user=id_user
		)
		session.add(nota)
		session.commit()
		session.refresh(nota)
		return jsonify({
			"ok": True,
			"data": {
				"id": nota.id,
				"tipo_salida": nota.tipo_salida,
				"motivo": nota.motivo,
				"id_user": nota.id_user,
				"created_at": str(nota.created_at)
			}
		}), 201
	except Exception as e:
		session.rollback()
		return jsonify({"ok": False, "message": str(e)}), 500
	finally:
		session.close()
