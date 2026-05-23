# database.py
# ============================================================
# MANEJO DE LA BASE DE DATOS (archivo JSON)
# ============================================================

import json
import os
import time  # <-- AGREGADO: necesario para obtener_compras_usuario_hoy

DB_FILE = "db.json"

def cargar_db():
    """Carga la base de datos desde el archivo JSON"""
    if not os.path.exists(DB_FILE):
        return {
            "pagos_pendientes": {},
            "entregados": []
        }
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"pagos_pendientes": {}, "entregados": []}

def guardar_db(db):
    """Guarda la base de datos en el archivo JSON"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def guardar_pago(pago_id, datos_pago):
    """Guarda un nuevo pago pendiente"""
    db = cargar_db()
    db["pagos_pendientes"][pago_id] = datos_pago
    return guardar_db(db)

def obtener_pago(pago_id):
    """Obtiene los datos de un pago por su ID"""
    db = cargar_db()
    return db["pagos_pendientes"].get(pago_id)

def actualizar_estado_pago(pago_id, nuevo_estado):
    """Actualiza el estado de un pago (pendiente, pagado, entregado)"""
    db = cargar_db()
    if pago_id in db["pagos_pendientes"]:
        db["pagos_pendientes"][pago_id]["estado"] = nuevo_estado
        if nuevo_estado == "entregado":
            db["entregados"].append(pago_id)
        return guardar_db(db)
    return False

def eliminar_pago(pago_id):
    """Elimina un pago (útil para limpieza)"""
    db = cargar_db()
    if pago_id in db["pagos_pendientes"]:
        del db["pagos_pendientes"][pago_id]
        return guardar_db(db)
    return False

# ============================================================
# NUEVAS FUNCIONES PARA LÍMITE DE COMPRAS
# ============================================================

def obtener_compras_usuario_hoy(user_id):
    """Retorna cuántos scripts ha comprado un usuario en las últimas 24 horas"""
    db = cargar_db()
    ahora = time.time()
    hace_24h = ahora - 86400
    
    compras_recientes = 0
    for pago_id, datos in db["pagos_pendientes"].items():
        if datos.get("user_id") == user_id and datos.get("estado") == "entregado":
            fecha_compra = datos.get("fecha", 0)
            if fecha_compra > hace_24h:
                compras_recientes += 1
    
    return compras_recientes

def limite_compras_por_usuario(user_id, limite=5):
    """Verifica si el usuario ha superado el límite de compras diarias"""
    compras_hoy = obtener_compras_usuario_hoy(user_id)
    return compras_hoy < limite