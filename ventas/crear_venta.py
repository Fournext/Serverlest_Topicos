from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
from models.detalle_venta import DetalleVenta
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def crear_venta(request):
	if request.method != "POST":
		return ("Method Not Allowed", 405)

	data = request.get_json(silent=True) or {}

	usuario_id = data.get("usuario_id")
	det_venta = data.get("det_venta")
	estado = data.get("estado", "pendiente")

	if not usuario_id or det_venta is None:
		return jsonify({"ok": False, "message": "Faltan campos"}), 400
    
	if not verificar_usuario(usuario_id):
		return jsonify({"ok": False, "message": "Usuario no existe"}), 400

	session = SessionLocal()

	try:
		venta = Venta(
			usario_id=usuario_id,
			estado=estado,
			total=0
		)

		session.add(venta)
		session.commit()
		session.refresh(venta)
        
		if isinstance(det_venta, dict):
			det_venta["venta_id"] = venta.id
			detalle_response = crear_detalle_venta(det_venta)
		elif isinstance(det_venta, list):
			detalle_response = []
			for item in det_venta:
				item["venta_id"] = venta.id
				detalle_response.append(crear_detalle_venta(item))

		if detalle_response is None:
			session.delete(venta)
			session.commit()
			return jsonify({"ok": False, "message": "Error al crear detalle venta"}), 400
        
		total = calcular_total(detalle_response)
		venta.total = total
		session.commit()
		session.refresh(venta)
		return jsonify({
			"id": venta.id,
			"usuario_id": venta.usario_id,
			"detalle_venta": detalle_response,
			"total": float(venta.total),
			"estado": venta.estado
		}), 201

	except IntegrityError:
		session.rollback()
		return jsonify({"ok": False, "message": "Error de integridad"}), 400

	finally:
		session.close()

def verificar_usuario(usuario_id):
	try:
		response = requests.get(f"{URLAPI}/usuario/obtener/{usuario_id}")
		if response.status_code == 200:
			return True
		return False
	except requests.RequestException:
		return False

def crear_detalle_venta(det_venta):
	try:
		response = requests.post(f"{URLAPI}/detalle_venta/crear", json=det_venta)
		if response.status_code == 201:
			return response.json()
		return None
	except requests.RequestException:
		return None

def calcular_total(det_venta):
	total = 0
	if isinstance(det_venta, dict):
		total += det_venta.get("subtotal", 0)
	elif isinstance(det_venta, list):
		for item in det_venta:
			total += item.get("subtotal", 0)
	return total
