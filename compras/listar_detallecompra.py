from flask import jsonify
from models.detalle_compra import DetalleCompra
from common.bd import SessionLocal
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def listar_detalle_compra(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    session = SessionLocal()
    try:
        compra_id = request.args.get("id")
        if not compra_id:
            path_parts = request.path.rstrip("/").split("/")
            compra_id = path_parts[-1]

        if not compra_id.isdigit():
            return jsonify({"ok": False, "message": "ID inválido"}), 400

        compra_id = int(compra_id)

        query = session.query(DetalleCompra).filter_by(compra_id=compra_id)
        detalles = query.all()

        detalles_list = []

        for d in detalles:
            producto = obtener_producto(d.producto_id)
            if not producto:
                return jsonify({"ok": False, "message": f"Producto {d.producto_id} no encontrado"}), 404

            detalles_list.append({
                "id": d.id,
                "compra_id": d.compra_id,
                "producto": producto,
                "precio_unitario": float(d.precio_unitario),
                "cantidad": d.cantidad,
                "subtotal": float(d.subtotal),
                "created_at": str(d.created_at)
            })

        return jsonify({"ok": True, "data": detalles_list}), 200

    finally:
        session.close()


def obtener_producto(producto_id):
    try:
        resp = requests.get(f"{URLAPI}/inventario/obtener/{producto_id}")
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None