from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def listar_ventas(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	usuario_id = request.args.get("usuario_id")
	if not usuario_id:
		data = request.get_json(silent=True) or {}
		usuario_id = data.get("usuario_id")

	if not usuario_id:
		return jsonify({"ok": False, "message": "Falta usuario_id"}), 400

	session = SessionLocal()
	try:
		ventas = session.query(Venta).filter(Venta.usuario_id == usuario_id, Venta.estado != "anulada").all()
		ventas_list = [
			{
				"id": v.id,
				"usuario_id": v.usuario_id,
				"total": float(v.total),
				"estado": v.estado
			}
			for v in ventas
		]
		return jsonify({"ok": True, "data": ventas_list}), 200
	finally:
		session.close()
