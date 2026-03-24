from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.venta import Venta
from common.bd import SessionLocal
from models.detalle_venta import DetalleVenta
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
        error_en_detalles = False

        for item in items_a_procesar:
            item["venta_id"] = nueva_venta.id
            resp = crear_detalle_venta(item)
            
            if resp:
                detalle_responses.append(resp)
                disminuir_stock(item.get("producto_id"), item.get("cantidad"))
            else:
                error_en_detalles = True
                break  
            
        if error_en_detalles or not detalle_responses:
            session.delete(nueva_venta)
            session.commit()
            return jsonify({"ok": False, "message": "Error al crear uno o varios detalles"}), 400
        
        total_final = calcular_total(detalle_responses)
        nueva_venta.total = total_final
        session.commit()
        session.refresh(nueva_venta)

        return jsonify({
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
  
def disminuir_stock(producto_id, cantidad):
	try:
		payload = {"producto_id": producto_id, "cantidad": cantidad}
		response = requests.put(f"{URLAPI}/inventario/disminuir_stock", json=payload)
		return response.status_code == 200
	except Exception:
		return False

def verificar_usuario(usuario_id):
	try:
		response = requests.get(f"http://localhost:8082/usuario/obtener/{usuario_id}")
		if response.status_code == 200:
			return True
		return False
	except requests.RequestException:
		return False

def crear_detalle_venta(det_venta):
	try:
		response = requests.post(f"http://localhost:8083/detalle_venta/crear", json=det_venta)
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