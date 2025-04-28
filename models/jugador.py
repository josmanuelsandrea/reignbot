from dataclasses import dataclass

@dataclass
class Jugador:
    id_usuario: int
    nombre_usuario: str
    reino: str
    rol: str
    es_rey: bool = False