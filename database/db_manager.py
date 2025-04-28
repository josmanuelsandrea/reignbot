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
                    nombre_partida TEXT,
                    fecha_inicio TEXT,
                    fecha_fin TEXT,
                    ganador TEXT
                )
            ''')

def agregar_jugador(usuario_id, nombre_usuario, reino, rol, es_rey=False):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT OR IGNORE INTO jugadores (usuario_id, nombre_usuario, reino, rol, es_rey)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario_id, nombre_usuario, reino, rol, es_rey))


def agregar_reino(nombre, territorio, soldados, oro, moral, alimentacion, defensa_base):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT OR IGNORE INTO reinos (nombre, territorio, soldados, oro, moral, alimentacion, defensa_base)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, territorio, soldados, oro, moral, alimentacion, defensa_base))


def obtener_reino(nombre_reino):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute('SELECT * FROM reinos WHERE nombre = ?', (nombre_reino,))
            return cur.fetchone()


def obtener_jugador(usuario_id):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute('SELECT * FROM jugadores WHERE usuario_id = ?', (usuario_id,))
            return cur.fetchone()

# Funciones adicionales para gestionar la partida

def obtener_reinos():
    """
    Devuelve una lista de diccionarios con todos los reinos y sus atributos.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute('SELECT * FROM reinos')
            return [dict(row) for row in cur.fetchall()]


def obtener_jugadores_por_reino(nombre_reino):
    """
    Devuelve una lista de diccionarios con los jugadores que pertenecen al reino.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            cur = conn.execute(
                'SELECT * FROM jugadores WHERE reino = ?', (nombre_reino,)
            )
            return [dict(row) for row in cur.fetchall()]


def actualizar_reino(nombre_reino, **kwargs):
    """
    Actualiza los campos de un reino. Uso: actualizar_reino('Eltaris', oro=600, moral=80)
    """
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
