from flask import Blueprint, jsonify, request
from app.db import get_connection, init_db

ventas_bp = Blueprint("ventas", __name__)



@ventas_bp.get("/")
def listar_ventas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    ventas = [dict(row) for row in rows]

    return jsonify({
        "modulo": "ventas",
        "total_registros": len(ventas),
        "items": ventas
    }), 200


@ventas_bp.get("/<int:venta_id>")
def obtener_venta(venta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Venta no encontrada"}), 404

    return jsonify(dict(row)), 200


@ventas_bp.post("/")
def crear_venta():
    data = request.get_json(silent=True) or {}

    cliente = data.get("cliente")
    producto = data.get("producto")
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")

    if not cliente or not producto:
        return jsonify({"error": "cliente y producto son obligatorios"}), 400

    if cantidad is None or precio_unitario is None:
        return jsonify({"error": "cantidad y precio_unitario son obligatorios"}), 400

    try:
        cantidad = int(cantidad)
        precio_unitario = float(precio_unitario)
    except (ValueError, TypeError):
        return jsonify({"error": "cantidad debe ser entero y precio_unitario numérico"}), 400

    if cantidad <= 0 or precio_unitario <= 0:
        return jsonify({"error": "cantidad y precio_unitario deben ser mayores a 0"}), 400

    total = cantidad * precio_unitario

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ventas (cliente, producto, cantidad, precio_unitario, total)
        VALUES (?, ?, ?, ?, ?)
    """, (cliente, producto, cantidad, precio_unitario, total))
    conn.commit()
    venta_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "mensaje": "Venta creada correctamente",
        "venta": {
            "id": venta_id,
            "cliente": cliente,
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "total": total
        }
    }), 201


@ventas_bp.put("/<int:venta_id>")
def actualizar_venta(venta_id):
    data = request.get_json(silent=True) or {}

    cliente = data.get("cliente")
    producto = data.get("producto")
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
    venta_actual = cursor.fetchone()

    if not venta_actual:
        conn.close()
        return jsonify({"error": "Venta no encontrada"}), 404

    cliente = cliente or venta_actual["cliente"]
    producto = producto or venta_actual["producto"]
    cantidad = cantidad if cantidad is not None else venta_actual["cantidad"]
    precio_unitario = precio_unitario if precio_unitario is not None else venta_actual["precio_unitario"]

    try:
        cantidad = int(cantidad)
        precio_unitario = float(precio_unitario)
    except (ValueError, TypeError):
        conn.close()
        return jsonify({"error": "cantidad debe ser entero y precio_unitario numérico"}), 400

    if cantidad <= 0 or precio_unitario <= 0:
        conn.close()
        return jsonify({"error": "cantidad y precio_unitario deben ser mayores a 0"}), 400

    total = cantidad * precio_unitario

    cursor.execute("""
        UPDATE ventas
        SET cliente = ?, producto = ?, cantidad = ?, precio_unitario = ?, total = ?
        WHERE id = ?
    """, (cliente, producto, cantidad, precio_unitario, total, venta_id))
    conn.commit()
    conn.close()

    return jsonify({
        "mensaje": "Venta actualizada correctamente",
        "venta": {
            "id": venta_id,
            "cliente": cliente,
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "total": total
        }
    }), 200


@ventas_bp.delete("/<int:venta_id>")
def eliminar_venta(venta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
    venta = cursor.fetchone()

    if not venta:
        conn.close()
        return jsonify({"error": "Venta no encontrada"}), 404

    cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "mensaje": "Venta eliminada correctamente",
        "id": venta_id
    }), 200