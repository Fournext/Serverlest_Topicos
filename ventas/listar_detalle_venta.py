from flask import jsonify
from models.detalle_venta import DetalleVenta
from common.bd import SessionLocal

def listar_detalle_venta(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    venta_id = request.args.get("venta_id")
    session = SessionLocal()
    try:
        query = session.query(DetalleVenta)
        if venta_id:
            query = query.filter_by(venta_id=venta_id)
        detalles = query.all()
        detalles_list = [
            {
                "id": d.id,
                "venta_id": d.venta_id,
                "producto_id": d.producto_id,
                "precio_unitario": float(d.precio_unitario),
                "cantidad": d.cantidad,
                "subtotal": float(d.subtotal),
                "created_at": str(d.created_at)
            }
            for d in detalles
        ]
        return jsonify({"ok": True, "data": detalles_list}), 200
    finally:
        session.close()
