"""Modelo Cliente."""

from dataclasses import dataclass


@dataclass
class Customer:
    """
    Modelo para el registro de un cliente en el sistema.
    Atributos: id, nombre, email, teléfono.
    """

    id: str
    name: str
    email: str
    phone: str = ""

    def to_dict(self) -> dict:
        """Convertimos a diccionario los datos del cliente."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        """Crea instancia."""
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
        )
