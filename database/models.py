# database/models.py
from peewee import (
    Model, SqliteDatabase,
    AutoField, IntegerField, CharField,
    ForeignKeyField, DateTimeField
)

from datetime import datetime
from config import REIGN_START_PROPS

# Conexión a la BD SQLite
db = SqliteDatabase('bot_reinos.db')


class BaseModel(Model):
    class Meta:
        database = db


class Partida(BaseModel):
    id = AutoField()
    guild_id = IntegerField(null=False)
    nombre = CharField(null=True)
    fecha_inicio = DateTimeField(default=datetime.now)
    fecha_fin = DateTimeField(null=True)
    estado = CharField(
        null=False,
        choices=[('esperando', 'esperando'), ('en_curso', 'en_curso'), ('finalizada', 'finalizada')],
        default='esperando'
    )


class Reino(BaseModel):
    id = AutoField()
    nombre = CharField(null=False)
    partida = ForeignKeyField(Partida, backref='reinos', on_delete='CASCADE')
    soldados = IntegerField(default=REIGN_START_PROPS['soldados'])  # soldados disponibles
    oro = IntegerField(default=REIGN_START_PROPS['oro'])  # oro disponible
    comida = IntegerField(default=REIGN_START_PROPS['comida'])  # comida disponible
    defensa_base = IntegerField(default=REIGN_START_PROPS['defensa_base'])  # defensa base del reino
    territorio = IntegerField(default=0)  # km² de territorio del reino
    


class Jugador(BaseModel):
    id = AutoField()
    usuario_id = IntegerField(null=False)
    nombre_usuario = CharField(null=True)
    partida = ForeignKeyField(Partida, backref='jugadores', on_delete='CASCADE')
    reino = ForeignKeyField(Reino, backref='jugadores', null=True, on_delete='SET NULL')
    se_unio_en = DateTimeField(default=datetime.now)
    
class JugadorRol(BaseModel):
    id       = AutoField()
    jugador  = ForeignKeyField(Jugador, backref='roles', on_delete='CASCADE')
    rol      = CharField()  # guardamos aquí el nombre de cada rol asignado


class Accion(BaseModel):
    id = AutoField()
    jugador = ForeignKeyField(Jugador, backref='acciones', on_delete='CASCADE')
    descripcion = CharField(null=False)
    fecha = DateTimeField(default=datetime.now)


def initialize_db():
    """Crea las tablas en la base de datos (si no existen)."""
    db.connect()
    db.create_tables([Partida, Reino, Jugador, JugadorRol, Accion])
    db.close()