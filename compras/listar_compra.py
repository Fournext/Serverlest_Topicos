from flask import jsonify
from sqlalchemy.exc import IntegrityError
from models.compra import Compra
from common.bd import SessionLocal
import requests
from dotenv import load_dotenv
import os

load_dotenv()
URLAPI = os.environ["URLAPI"]

def listar_compras(request):
    if request.method != "GET":
        return ("Method Not Allowed", 405)

    session = SessionLocal()
    try:
        usuario_id = request.args.get("id")
        if not usuario_id:
            path_parts = request.path.rstrip("/").split("/")
            usuario_id = path_parts[-1]

        if not usuario_id.isdigit():
            return jsonify({"ok": False, "message": "ID inválido"}), 400

        usuario_id = int(usuario_id)
        
        usuario = verificar_usuario(usuario_id)
        if not usuario:
            return jsonify({"ok": False, "message": "Usuario no existe"}), 400
        
        compras = session.query(Compra).filter(Compra.usuario_id == usuario_id, Compra.estado != "anulada").all()
        compras_list = [
            {
                "id": c.id,
                "usuario": usuario,
                "total": float(c.total),
                "estado": c.estado
            }
            for c in compras
        ]
        return jsonify({"ok": True, "data": compras_list}), 200
    finally:
        session.close()

def verificar_usuario(usuario_id):
    try:
        response = requests.get(f"{URLAPI}/usuario/obtener/{usuario_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None
