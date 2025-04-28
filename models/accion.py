from dataclasses import dataclass

@dataclass
class Accion:
    nombre: str
    descripcion: str
    rol_requerido: str
    efecto: str
    cooldown_horas: int