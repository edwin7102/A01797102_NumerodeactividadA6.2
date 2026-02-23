"""Servicio de reservaciones: Create, Delete."""

import uuid
from models.reservation import Reservation
from storage.manager import StorageManager


class ReservationService:
    """Servicio para manejo de reservaciones."""

    def __init__(self, storage=None):
        self.storage = storage or StorageManager()

    def create_reservation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, customer_id, hotel_id, room_number, check_in, check_out
    ):
        """Create"""
        customers = self.storage.load_customers()
        hotels = self.storage.load_hotels()
        if not any(c["id"] == customer_id for c in customers):
            return None
        hotel_idx = next((i for i, h in enumerate(hotels) if h["id"] == hotel_id), None)
        if hotel_idx is None:
            return None

        hotel = hotels[hotel_idx]
        reserved = set(hotel.get("reserved_rooms", []))
        if room_number < 1 or room_number > hotel["total_rooms"] or room_number in reserved:
            return None

        reservation_id = str(uuid.uuid4())
        reservation = Reservation(
            id=reservation_id,
            customer_id=customer_id,
            hotel_id=hotel_id,
            room_number=room_number,
            check_in=check_in,
            check_out=check_out,
        )

        reservations = self.storage.load_reservations()
        reservations.append(reservation.to_dict())
        self.storage.save_reservations(reservations)

        reserved.add(room_number)
        hotels[hotel_idx]["reserved_rooms"] = list(reserved)
        self.storage.save_hotels(hotels)

        return reservation

    def cancel_reservation(self, reservation_id):
        """Delete"""
        reservations = self.storage.load_reservations()
        hotels = self.storage.load_hotels()

        res = None
        for r in reservations:
            if r["id"] == reservation_id and r.get("status") == "active":
                res = r
                break
        if not res:
            return False

        hotel_id = res["hotel_id"]
        room_number = res["room_number"]
        for i, h in enumerate(hotels):
            if h["id"] == hotel_id:
                reserved = set(h.get("reserved_rooms", []))
                reserved.discard(room_number)
                hotels[i]["reserved_rooms"] = list(reserved)
                self.storage.save_hotels(hotels)
                break

        for i, r in enumerate(reservations):
            if r["id"] == reservation_id:
                reservations[i]["status"] = "cancelled"
                self.storage.save_reservations(reservations)
                return True
        return False
