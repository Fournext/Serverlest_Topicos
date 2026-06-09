from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
from dotenv import load_dotenv
import os
import requests

load_dotenv()
URLAPI = os.environ["URLAPI"]

def listar_ventas(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)


	session = SessionLocal()
	try:
		usuario_id = request.args.get("id")
		if not usuario_id:
			path_parts = request.path.rstrip("/").split("/")
			usuario_id = path_parts[-1]

		if not usuario_id.isdigit():
			return jsonify({"ok": False, "message": "ID inválido"}), 400

		usuario_id = int(usuario_id)
        
		usuario = verificar_usuario(usuario_id)
		if not usuario:
			return jsonify({"ok": False, "message": "Usuario no existe"}), 400
		
		ventas = session.query(Venta).filter(Venta.usuario_id == usuario_id, Venta.estado != "anulada").all()
		ventas_list = [
			{
				"id": v.id,
				"usuario_id": v.usuario_id,
				"detalle_venta": obtener_detalle_venta(v.id),
				"total": float(v.total),
				"estado": v.estado
			}
			for v in ventas
		]
		return jsonify({"ok": True, "data": ventas_list}), 200
	finally:
		session.close()

def verificar_usuario(usuario_id):
    try:
        response = requests.get(f"{URLAPI}/usuario/obtener/{usuario_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def obtener_detalle_venta(venta_id):
    try:
        response = requests.get(f"{URLAPI}/detalle_venta/listar/{venta_id}")
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, dict) and res_json.get("ok"):
                return res_json.get("data", [])
            return res_json
        return []
    except requests.RequestException:
        return []
