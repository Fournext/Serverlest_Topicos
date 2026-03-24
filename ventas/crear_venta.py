from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]


def crear_venta(request):
    if request.method != "POST":
        return ("Method Not Allowed", 405)

    data = request.get_json(silent=True) or {}
    usuario_id = data.get("usuario_id")
    det_venta = data.get("det_venta")
    estado = data.get("estado", "pendiente")

    if not usuario_id or det_venta is None:
        return jsonify({"ok": False, "message": "Faltan campos"}), 400

    if not verificar_usuario(usuario_id):
        return jsonify({"ok": False, "message": "Usuario no existe"}), 400

    items_a_procesar = det_venta if isinstance(det_venta, list) else [det_venta]

    if not items_a_procesar:
        return jsonify({"ok": False, "message": "No hay detalles para procesar"}), 400

    # 1. Validar estructura mínima
    for item in items_a_procesar:
        producto_id = item.get("producto_id")
        cantidad = item.get("cantidad")

        if not producto_id or cantidad is None:
            return jsonify({"ok": False, "message": "Cada detalle debe tener producto_id y cantidad"}), 400

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return jsonify({"ok": False, "message": f"La cantidad del producto {producto_id} debe ser mayor a 0"}), 400
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": f"La cantidad del producto {producto_id} no es válida"}), 400

    # 2. Agrupar productos repetidos y sumar cantidades
    productos_agrupados = agrupar_cantidades_por_producto(items_a_procesar)

    # 3. Validar stock total por producto
    validacion_stock = validar_stock_productos(productos_agrupados)
    if not validacion_stock["ok"]:
        return jsonify(validacion_stock), 400

    session = SessionLocal()
    try:
        nueva_venta = Venta(
            usuario_id=usuario_id,
            estado=estado,
            total=0
        )
        session.add(nueva_venta)
        session.commit()
        session.refresh(nueva_venta)

        detalle_responses = []

        for item in items_a_procesar:
            item_payload = dict(item)
            item_payload["venta_id"] = nueva_venta.id

            resp = crear_detalle_venta(item_payload)

            if not resp:
                session.delete(nueva_venta)
                session.commit()
                return jsonify({"ok": False, "message": "Error al crear uno o varios detalles"}), 400

            detalle_responses.append(resp)

            ok_stock = disminuir_stock(item.get("producto_id"), item.get("cantidad"))
            if not ok_stock:
                session.delete(nueva_venta)
                session.commit()
                return jsonify({
                    "ok": False,
                    "message": f"No se pudo disminuir stock del producto {item.get('producto_id')}"
                }), 400

        total_final = calcular_total(detalle_responses)
        nueva_venta.total = total_final
        session.commit()
        session.refresh(nueva_venta)

        return jsonify({
            "ok": True,
            "id": nueva_venta.id,
            "usuario_id": nueva_venta.usuario_id,
            "detalle_venta": detalle_responses,
            "total": float(nueva_venta.total),
            "estado": nueva_venta.estado
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"ok": False, "message": "Error de integridad en la base de datos"}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"ok": False, "message": f"Error inesperado: {str(e)}"}), 500
    finally:
        session.close()


def agrupar_cantidades_por_producto(items):
    productos = {}

    for item in items:
        producto_id = int(item["producto_id"])
        cantidad = int(item["cantidad"])

        if producto_id not in productos:
            productos[producto_id] = 0

        productos[producto_id] += cantidad

    return productos


def validar_stock_productos(productos_agrupados):
    productos_validados = []

    for producto_id, cantidad_total in productos_agrupados.items():
        producto = obtener_producto(producto_id)

        if not producto:
            return {
                "ok": False,
                "message": f"Producto {producto_id} no existe"
            }

        stock_actual = producto.get("stock_actual", 0)
        nombre = producto.get("nombre", f"Producto {producto_id}")

        try:
            stock_actual = int(stock_actual)
        except (TypeError, ValueError):
            stock_actual = 0

        if stock_actual < cantidad_total:
            return {
                "ok": False,
                "message": f"Stock insuficiente para {nombre}",
                "producto": {
                    "id": producto_id,
                    "nombre": nombre,
                    "stock_actual": stock_actual,
                    "cantidad_solicitada": cantidad_total
                }
            }

        productos_validados.append({
            "id": producto_id,
            "nombre": nombre,
            "stock_actual": stock_actual,
            "cantidad_solicitada": cantidad_total
        })

    return {
        "ok": True,
        "productos_validados": productos_validados
    }


def disminuir_stock(producto_id, cantidad):
    try:
        payload = {"producto_id": producto_id, "cantidad": cantidad}
        response = requests.put(f"{URLAPI}/inventario/disminuir_stock", json=payload)
        return response.status_code == 200
    except Exception:
        return False


def verificar_usuario(usuario_id):
    try:
        response = requests.get(f"{URLAPI}/usuario/obtener/{usuario_id}")
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False


def crear_detalle_venta(det_venta):
    try:
        response = requests.post(f"{URLAPI}/venta/crear_detalle_venta", json=det_venta)
        if response.status_code == 201:
            return response.json()
        return None
    except requests.RequestException:
        return None


def calcular_total(det_venta):
    print("DEBUG - Datos recibidos en calcular_total:", det_venta)
    total = 0.0
    items = det_venta if isinstance(det_venta, list) else [det_venta]

    for item in items:
        if isinstance(item, dict) and "data" in item:
            datos_producto = item.get("data", {})
            subtotal = datos_producto.get("subtotal", 0)
            try:
                total += float(subtotal)
            except (ValueError, TypeError):
                precio = float(datos_producto.get("precio_unitario", 0))
                cantidad = float(datos_producto.get("cantidad", 0))
                total += (precio * cantidad)
        else:
            print("DEBUG - El item no tiene el formato esperado {'data': {...}}")

    return total


def obtener_producto(producto_id):
    try:
        resp = requests.get(f"{URLAPI}/inventario/obtener/{producto_id}")
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None