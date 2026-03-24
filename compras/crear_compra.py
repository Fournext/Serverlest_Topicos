
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def crear_compra(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    usuario_id = data.get("usuario_id")
    det_compra = data.get("det_compra")
    estado = data.get("estado", "pendiente")

    if not usuario_id or det_compra is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400
    
    if not verificar_usuario(usuario_id):
        return jsonify({"ok": False, "message": "Usuario no existe"}), 400

    session = SessionLocal()

    try:
        compra = Compra(
            usuario_id=usuario_id,
            estado=estado,
            total=0
        )

        session.add(compra)
        session.commit()
        session.refresh(compra)
        
        if isinstance(det_compra, dict):
            det_compra["compra_id"] = compra.id
            detalle_response = crear_detalle_compra(det_compra)
        elif isinstance(det_compra, list):
            detalle_response = []
            for item in det_compra:
                item["compra_id"] = compra.id
                detalle_response.append(crear_detalle_compra(item))

        if detalle_response is None:
            session.delete(compra)
            session.commit()
            return jsonify({"ok": False, "message": "Error al crear detalle compra"}), 400
        
        total = calcular_total(detalle_response)
        compra.total = total
        session.commit()
        session.refresh(compra)
        return jsonify(
            {
                "id": compra.id,
                "usuario_id": compra.usuario_id,
                "detalle_compra": detalle_response,
                "total": float(compra.total),
                "estado": compra.estado
            }
        ), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400

    finally:
        session.close()
        
def crear_detalle_compra(compra_id, producto_id, precio_unitario, cantidad):
    try:
        payload = {
            "compra_id": compra_id,
            "producto_id": producto_id,
            "precio_unitario": precio_unitario,
            "cantidad": cantidad
        }
        resp = requests.post("https://southamerica-east1-gen-lang-client-0878332190.cloudfunctions.net/compras/crear_detalle", json=payload)
        if resp.status_code == 201:
            return resp.json().get("data")
        return {"error": "No se pudo crear el detalle de compra"}
    except Exception:
        return {"error": "Error al conectar con el servicio de detalle de compra"}


def verificar_usuario(usuario_id):
    try:
        response = requests.get(f"{URLAPI}/usuario/obtener/{usuario_id}")
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False
    
def crear_detalle_compra(det_compra):
    try:
        response = requests.post(f"{URLAPI}/detalle_compra/crear", json=det_compra)
        if response.status_code == 201:
            return response.json()
        return None
    except requests.RequestException:
        return None
    
def calcular_total(det_compra):
    total = 0
    print("Calculando total para detalle compra:", det_compra)
    if isinstance(det_compra, dict):
        total += det_compra.get("subtotal", 0)
        print("Subtotal del detalle compra:", det_compra.get("subtotal", 0))
    elif isinstance(det_compra, list):
        for item in det_compra:
            total += item.get("subtotal", 0)
            print("Subtotal del detalle compra:", item.get("subtotal", 0))
    return total
