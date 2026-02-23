"""Modelo Reservation."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Reservation:
    """
    Representa una reservación asociando un Cliente y un Hotel.
    Atributos: id, customer_id, hotel_id, room_number, check_in, check_out, status.
    """

    id: str
    customer_id: str
    hotel_id: str
    room_number: int
    check_in: date
    check_out: date
    status: str = "active"

    def to_dict(self) -> dict:
        """Pasamos a diccionario los datos de la reservación."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "room_number": self.room_number,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reservation":
        """Crea instancia."""
        return cls(
            id=data["id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            room_number=data["room_number"],
            check_in=date.fromisoformat(data["check_in"]),
            check_out=date.fromisoformat(data["check_out"]),
            status=data.get("status", "active"),
        )
