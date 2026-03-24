from flask import jsonify
from models.detalle_venta import DetalleVenta
from common.bd import SessionLocal

def anular_detalle_venta(request):
    if request.method != "PUT":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}
    detalle_id = data.get("id")
    if not detalle_id:
        return jsonify({"ok": False, "message": "Falta id del detalle"}), 400

    session = SessionLocal()
    try:
        detalle = session.query(DetalleVenta).filter_by(id=detalle_id).first()
        if not detalle:
            return jsonify({"ok": False, "message": "Detalle de venta no encontrado"}), 404
        detalle.estado = "anulado"
        session.commit()
        return jsonify({"ok": True, "message": "Detalle de venta anulado", "data": {
            "id": detalle.id,
            "venta_id": detalle.venta_id,
            "producto_id": detalle.producto_id,
            "precio_unitario": float(detalle.precio_unitario),
            "cantidad": detalle.cantidad,
            "subtotal": float(detalle.subtotal),
            "created_at": str(detalle.created_at)
        }}), 200
    finally:
        session.close()
