"""Servicio de hoteles: Create, Delete, Display, Update, Reserve, Cancel."""

import uuid
from models.hotel import Hotel
from storage.manager import StorageManager


class HotelService:
    """Servicio para manejo de hoteles."""

    def __init__(self, storage=None):
        self.storage = storage or StorageManager()

    def create_hotel(self, name, address, total_rooms):
        """Create"""
        hotel_id = str(uuid.uuid4())
        hotel = Hotel(
            id=hotel_id,
            name=name,
            address=address,
            total_rooms=total_rooms,
            reserved_rooms=set(),
        )
        hotels = self.storage.load_hotels()
        hotels.append(hotel.to_dict())
        self.storage.save_hotels(hotels)
        return hotel

    def delete_hotel(self, hotel_id):
        """Delete"""
        hotels = self.storage.load_hotels()
        original = len(hotels)
        hotels = [h for h in hotels if h["id"] != hotel_id]
        if len(hotels) < original:
            self.storage.save_hotels(hotels)
            return True
        return False

    def display_hotel(self, hotel_id):
        """Find by id"""
        hotel = self.get_hotel(hotel_id)
        if not hotel:
            return None
        lines = [
            f"Hotel: {hotel.name}",
            f"  ID: {hotel.id}",
            f"  Dirección: {hotel.address}",
            f"  Habitaciones: {hotel.available_rooms}/{hotel.total_rooms} "
            f"disponibles",
        ]
        return "\n".join(lines)

    def update_hotel(self, hotel_id, name=None, address=None,
                     total_rooms=None):
        """Update"""
        hotels = self.storage.load_hotels()
        for i, h in enumerate(hotels):
            if h["id"] == hotel_id:
                if name is not None:
                    hotels[i]["name"] = name
                if address is not None:
                    hotels[i]["address"] = address
                if total_rooms is not None:
                    hotels[i]["total_rooms"] = total_rooms
                self.storage.save_hotels(hotels)
                return Hotel.from_dict(hotels[i])
        return None

    def reserve_room(self, hotel_id, room_number):
        """Registrar reservación"""
        hotels = self.storage.load_hotels()
        for i, h in enumerate(hotels):
            if h["id"] == hotel_id:
                reserved = set(h.get("reserved_rooms", []))
                if (room_number < 1 or room_number > h["total_rooms"]
                        or room_number in reserved):
                    return False
                reserved.add(room_number)
                hotels[i]["reserved_rooms"] = list(reserved)
                self.storage.save_hotels(hotels)
                return True
        return False

    def cancel_reservation(self, hotel_id, room_number):
        """Liberar reservación)"""
        hotels = self.storage.load_hotels()
        for i, h in enumerate(hotels):
            if h["id"] == hotel_id:
                reserved = set(h.get("reserved_rooms", []))
                if room_number in reserved:
                    reserved.discard(room_number)
                    hotels[i]["reserved_rooms"] = list(reserved)
                    self.storage.save_hotels(hotels)
                    return True
                return False
        return False

    def get_hotel(self, hotel_id):
        """Obtiene un hotel por ID."""
        hotels = self.storage.load_hotels()
        for h in hotels:
            if h["id"] == hotel_id:
                return Hotel.from_dict(h)
        return None
