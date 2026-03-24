

from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.detalle_compra import DetallaCompra
from common.bd import SessionLocal
import requests

def crear_detalle_compra(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}

    compra_id = data.get("compra_id")
    producto_id = data.get("producto_id")
    precio_unitario = data.get("precio_unitario")
    cantidad = data.get("cantidad")
    estado = data.get("estado", "activo")

    if not all([compra_id, producto_id, precio_unitario, cantidad]):
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    producto = obtener_producto(producto_id)
    if not producto:
        return jsonify({"ok": False, "message": "Producto no encontrado"}), 404

    try:
        subtotal = float(precio_unitario) * int(cantidad)
    except Exception:
        return jsonify({"ok": False, "message": "precio_unitario o cantidad inválidos"}), 400

    session = SessionLocal()
    try:
        detalle = DetallaCompra(
            compra_id=compra_id,
            producto_id=producto_id,
            estado=estado,
            precio_unitario=precio_unitario,
            cantidad=cantidad,
            subtotal=subtotal
        )
        session.add(detalle)
        session.commit()
        session.refresh(detalle)
        return jsonify({
            "ok": True,
            "data": {
                "id": detalle.id,
                "compra_id": detalle.compra_id,
                "producto_id": detalle.producto_id,
                "estado": detalle.estado,
                "precio_unitario": float(detalle.precio_unitario),
                "cantidad": detalle.cantidad,
                "subtotal": float(detalle.subtotal),
                "created_at": str(detalle.created_at),
                "producto": producto
            }
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400
    finally:
        session.close()


def obtener_producto(producto_id):
    try:
        resp = requests.get(f"https://southamerica-east1-gen-lang-client-0878332190.cloudfunctions.net/inventario/obtenerproducto/{producto_id}")
        if resp.status_code == 200:
            return resp.json().get("data")
        return None
    except Exception:
        return None