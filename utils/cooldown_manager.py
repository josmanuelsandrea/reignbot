import time

# Un diccionario para guardar los cooldowns: { (usuario_id, accion): tiempo_de_uso }
cooldowns = {}

# Tiempo actual en segundos
current_time = lambda: int(time.time())

# --- Función para verificar si un usuario tiene cooldown activo ---
def tiene_cooldown(usuario_id: int, accion: str, cooldown_segundos: int) -> bool:
    clave = (usuario_id, accion)
    ultimo_uso = cooldowns.get(clave, 0)
    return current_time() < ultimo_uso + cooldown_segundos

# --- Función para registrar el uso de una acción por un usuario ---
def registrar_uso(usuario_id: int, accion: str):
    clave = (usuario_id, accion)
    cooldowns[clave] = current_time()

# --- Función para obtener el tiempo restante de cooldown ---
def tiempo_restante(usuario_id: int, accion: str, cooldown_segundos: int) -> int:
    clave = (usuario_id, accion)
    ultimo_uso = cooldowns.get(clave, 0)
    restante = (ultimo_uso + cooldown_segundos) - current_time()
    return max(restante, 0)