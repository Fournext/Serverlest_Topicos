from flask import jsonify
from models.detalle_venta import DetalleVenta
from common.bd import SessionLocal

def crear_detalle_venta(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}
    venta_id = data.get("venta_id")
    producto_id = data.get("producto_id")
    precio_unitario = data.get("precio_unitario")
    cantidad = data.get("cantidad")
    estado = data.get("estado", "activo")

    if not venta_id or not producto_id or precio_unitario is None or cantidad is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    subtotal = float(precio_unitario) * int(cantidad)

    session = SessionLocal()
    try:
        detalle = DetalleVenta(
            venta_id=venta_id,
            producto_id=producto_id,
            precio_unitario=precio_unitario,
            cantidad=cantidad,
            subtotal=subtotal,
            estado=estado
        )
        session.add(detalle)
        session.commit()
        session.refresh(detalle)
        return jsonify({"ok": True, "data": {
            "id": detalle.id,
            "venta_id": detalle.venta_id,
            "producto_id": detalle.producto_id,
            "precio_unitario": float(detalle.precio_unitario),
            "cantidad": detalle.cantidad,
            "subtotal": float(detalle.subtotal),
            "estado": detalle.estado,
            "created_at": str(detalle.created_at)
        }}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"ok": False, "message": str(e)}), 400
    finally:
        session.close()
