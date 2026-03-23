from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.detalle_compra import DetalleCompra
from common.bd import SessionLocal
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def crear_detalle_compra(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)
    
    data = request.get_json(silent=True) or {}

    compra_id = data.get("compra_id")
    producto_id = data.get("producto_id")
    precio_unitario = data.get("precio_unitario")
    cantidad = data.get("cantidad", 1)

    if not compra_id or not producto_id or precio_unitario is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400
    
    session = SessionLocal()

    try:
        detalle_compra = DetalleCompra(
            compra_id=compra_id,
            producto_id=producto_id,
            precio_unitario=precio_unitario,
            cantidad=cantidad,
            subtotal=precio_unitario * cantidad
        )

        session.add(detalle_compra)
        session.commit()
        session.refresh(detalle_compra)

        if not aumentar_stock_producto(producto_id, cantidad):
            session.deldetalete(detalle_compra)
            session.commit()
            return jsonify({"ok": False, "message": "Error al aumentar stock del producto"}), 400

        return jsonify(
            {
                "id": detalle_compra.id,
                "compra_id": detalle_compra.compra_id,
                "producto_id": detalle_compra.producto_id,
                "precio_unitario": float(detalle_compra.precio_unitario),
                "cantidad": detalle_compra.cantidad,
                "subtotal": float(detalle_compra.subtotal)
            }
        ), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400
    finally:        
        session.close()

def aumentar_stock_producto(producto_id, cantidad):
    try:
        response = requests.put(f"{URLAPI}/inventario/aumentar_stock", json={"id": producto_id, "cantidad": cantidad})
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print("Error al aumentar stock:", e)
        return False