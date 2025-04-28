from dataclasses import dataclass

@dataclass
class EventoEspecial:
    nombre: str
    descripcion: str
    probabilidad: int
    efecto: str