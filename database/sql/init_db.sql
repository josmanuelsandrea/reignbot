-- init_db.sql
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER UNIQUE,
    nombre_usuario TEXT,
    reino TEXT,
    rol TEXT,
    es_rey BOOLEAN
);

CREATE TABLE IF NOT EXISTS reinos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE,
    territorio INTEGER,
    soldados INTEGER,
    oro INTEGER,
    moral INTEGER,
    alimentacion INTEGER,
    defensa_base INTEGER
);

CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER UNIQUE,
    nombre_partida TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    ganador TEXT
);
