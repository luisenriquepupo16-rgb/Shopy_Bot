# handlers/comunes.py
import random

def generar_monto_unico(precio_base):
    """
    Genera un monto único añadiendo 0.01 a 0.99 centavos aleatorios.
    El monto final se redondea a 2 decimales.
    """
    centavos_extra = random.randint(1, 99) / 100
    monto_final = precio_base + centavos_extra
    return round(monto_final, 2)