"""Modelo Hotel."""

from dataclasses import dataclass


@dataclass
class Hotel:
    """
    Modelo para el registro de un hotel en el sistema.
    Atributos: id, nombre, dirección, total de habitaciones y habitaciones reservadas.
    """

    id: str
    name: str
    address: str
    total_rooms: int
    reserved_rooms: set

    def __post_init__(self):
        if self.reserved_rooms is None:
            self.reserved_rooms = set()

    @property
    def available_rooms(self) -> int:
        return self.total_rooms - len(self.reserved_rooms)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "total_rooms": self.total_rooms,
            "reserved_rooms": list(self.reserved_rooms),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Hotel":
        return cls(
            id=data["id"],
            name=data["name"],
            address=data["address"],
            total_rooms=data["total_rooms"],
            reserved_rooms=set(data.get("reserved_rooms", [])),
        )
