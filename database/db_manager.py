import sqlite3
from contextlib import closing

DB_NAME = 'bot_reinos.db'

def inicializar_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jugadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER UNIQUE,
                    nombre_usuario TEXT,
                    reino TEXT,
                    rol TEXT,
                    es_rey BOOLEAN
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reinos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE,
                    territorio INTEGER,
                    soldados INTEGER,
                    oro INTEGER,
                    moral INTEGER,
                    alimentacion INTEGER,
                    defensa_base INTEGER
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS partidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER UNIQUE,
                    nombre_partida TEXT,
                    fecha_inicio TEXT,
                    fecha_fin TEXT,
                    ganador TEXT
                )
            ''')

# Jugadores
def agregar_jugador(usuario_id, nombre_usuario, reino, rol, es_rey=False):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT OR IGNORE INTO jugadores
                (usuario_id, nombre_usuario, reino, rol, es_rey)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario_id, nombre_usuario, reino, rol, es_rey))

# Reinos
def agregar_reino(nombre, territorio, soldados, oro, moral, alimentacion, defensa_base):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT OR IGNORE INTO reinos
                (nombre, territorio, soldados, oro, moral, alimentacion, defensa_base)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, territorio, soldados, oro, moral, alimentacion, defensa_base))

# Obtener un reino específico
def obtener_reino(nombre_reino):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute(
                'SELECT * FROM reinos WHERE nombre = ?', (nombre_reino,)
            )
            return cur.fetchone()

# Obtener un jugador específico
def obtener_jugador(usuario_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute(
                'SELECT * FROM jugadores WHERE usuario_id = ?', (usuario_id,)
            )
            return cur.fetchone()

# Listar todos los reinos
def obtener_reinos():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute('SELECT * FROM reinos')
            return [dict(row) for row in cur.fetchall()]

# Listar jugadores por reino
def obtener_jugadores_por_reino(nombre_reino):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute(
                'SELECT * FROM jugadores WHERE reino = ?', (nombre_reino,)
            )
            return [dict(row) for row in cur.fetchall()]

# Actualizar campos de un reino
def actualizar_reino(nombre_reino, **kwargs):
    if not kwargs:
        return
    campos = ', '.join(f"{k} = ?" for k in kwargs)
    valores = list(kwargs.values())
    valores.append(nombre_reino)
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute(
                f'UPDATE reinos SET {campos} WHERE nombre = ?',
                valores
            )

# NUEVAS FUNCIONES: Partidas por servidor
def crear_partida(guild_id, nombre_partida, fecha_inicio, fecha_fin=None, ganador=None):
    """
    Crea o reemplaza la partida activa para el servidor dado (guild_id).
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT OR REPLACE INTO partidas
                (guild_id, nombre_partida, fecha_inicio, fecha_fin, ganador)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, nombre_partida, fecha_inicio, fecha_fin, ganador))


def obtener_partida(guild_id):
    """
    Devuelve la partida activa para el servidor dado, o None si no existe.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute(
                'SELECT * FROM partidas WHERE guild_id = ?', (guild_id,)
            )
            return cur.fetchone()
