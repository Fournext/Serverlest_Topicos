from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.detalle_compra import DetalleCompra
from common.bd import SessionLocal
import requests

def listar_detalle_compra(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)
    
    session = SessionLocal()

    try: 
        detalles = session.query(DetalleCompra).all()

        data = [
            {
                "id": d.id,
                "compra_id": d.compra_id,
                "producto_id": d.producto_id,
                "precio_unitario": float(d.precio_unitario),
                "cantidad": d.cantidad,
                "subtotal": float(d.subtotal)
            }
            for d in detalles
        ]

        return jsonify({"ok": True, "data": data}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad"}), 400
    finally:        
        session.close()

