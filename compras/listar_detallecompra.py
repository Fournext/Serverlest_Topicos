from flask import jsonify
from models.detalle_compra import DetallaCompra
from common.bd import SessionLocal

def listar_detallecompra(request):
	if request.method != "GET":
		return ("Method Not Allowed", 405)

	compra_id = request.args.get("compra_id")
	session = SessionLocal()
	try:
		query = session.query(DetallaCompra)
		if compra_id:
			query = query.filter_by(compra_id=compra_id)
		detalles = query.all()
		detalles_list = [
			{
				"id": d.id,
				"compra_id": d.compra_id,
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
