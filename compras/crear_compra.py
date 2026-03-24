
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests


def crear_compra(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    usuario_id = data.get("usuario_id")
    total = data.get("total")
    estado = data.get("estado", "pendiente")

    detalles = data.get("detalles", [])

    if not usuario_id or total is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    if not verificar_usuario(usuario_id):
        return jsonify({"ok": False, "message": "El usuario no existe"}), 404

    session = SessionLocal()

    try:
        compra = Compra(
            usuario_id=usuario_id,
            total=total,
            estado=estado
        )

        session.add(compra)
        session.commit()
        session.refresh(compra)

        detalles_creados = []
        for detalle in detalles:
            producto_id = detalle.get("producto_id")
            precio_unitario = detalle.get("precio_unitario")
            cantidad = detalle.get("cantidad")
            if all([producto_id, precio_unitario, cantidad]):
                detalle_resp = crear_detalle_compra(
                    compra.id, producto_id, precio_unitario, cantidad
                )
                detalles_creados.append(detalle_resp)

        response_data = {
            "id": compra.id,
            "usuario_id": compra.usuario_id,
            "total": float(compra.total),
            "estado": compra.estado,
            "detalles": detalles_creados
        }

        return jsonify({
            "ok": True,
            "data": response_data
        }), 201

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
        response = requests.get(f"https://southamerica-east1-gen-lang-client-0878332190.cloudfunctions.net/usuarios/{usuario_id}")
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False