"""Tests para Reservation y ReservationService."""

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from models.reservation import Reservation
from services.hotel_service import HotelService
from services.customer_service import CustomerService
from services.reservation_service import ReservationService
from storage.manager import StorageManager


class TestReservationModel(unittest.TestCase):
    """Tests del modelo Reservation."""

    def test_reservation_creation(self):
        """Reservation se crea con atributos correctos."""
        check_in = date(2025, 3, 1)
        check_out = date(2025, 3, 5)
        r = Reservation(
            id="r1",
            customer_id="c1",
            hotel_id="h1",
            room_number=101,
            check_in=check_in,
            check_out=check_out,
        )
        self.assertEqual(r.id, "r1")
        self.assertEqual(r.customer_id, "c1")
        self.assertEqual(r.room_number, 101)
        self.assertEqual(r.status, "active")

    def test_reservation_to_dict_from_dict(self):
        """to_dict y from_dict son inversos."""
        check_in = date(2025, 3, 1)
        check_out = date(2025, 3, 5)
        r = Reservation(
            id="r1",
            customer_id="c1",
            hotel_id="h1",
            room_number=101,
            check_in=check_in,
            check_out=check_out,
        )
        r2 = Reservation.from_dict(r.to_dict())
        self.assertEqual(r.id, r2.id)
        self.assertEqual(r.check_in, r2.check_in)


class TestReservationService(unittest.TestCase):
    """Tests de ReservationService con persistencia."""

    def setUp(self):
        """Directorio temporal y datos de prueba."""
        self.tmpdir = tempfile.mkdtemp()
        self.storage = StorageManager(Path(self.tmpdir))
        self.hotel_svc = HotelService(self.storage)
        self.customer_svc = CustomerService(self.storage)
        self.reservation_svc = ReservationService(self.storage)
        self.hotel = self.hotel_svc.create_hotel("Madrid", "Addr", 10)
        self.customer = self.customer_svc.create_customer("Vinicius Jr",
                                                          "vinicius@tecmna.com")

    def test_create_reservation(self):
        """create_reservation crea y marca habitación."""
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        r = self.reservation_svc.create_reservation(
            self.customer.id,
            self.hotel.id,
            1,
            check_in,
            check_out,
        )
        self.assertIsNotNone(r)
        self.assertEqual(r.customer_id, self.customer.id)
        self.assertEqual(r.hotel_id, self.hotel.id)
        hotel = self.hotel_svc.get_hotel(self.hotel.id)
        self.assertEqual(hotel.available_rooms, 9)
        self.assertIn(1, hotel.reserved_rooms)

    def test_create_reservation_invalid_customer(self):
        """create_reservation retorna None si cliente no existe."""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        r = self.reservation_svc.create_reservation(
            "cliente-inexistente", self.hotel.id, 1, check_in, check_out
        )
        self.assertIsNone(r)

    def test_create_reservation_invalid_hotel(self):
        """create_reservation retorna None si hotel no existe."""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        r = self.reservation_svc.create_reservation(
            self.customer.id, "hotel-inexistente", 1, check_in, check_out
        )
        self.assertIsNone(r)

    def test_create_reservation_room_taken(self):
        """create_reservation retorna None si habitación ocupada."""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        self.reservation_svc.create_reservation(
            self.customer.id, self.hotel.id, 1, check_in, check_out
        )
        r2 = self.reservation_svc.create_reservation(
            self.customer.id,
            self.hotel.id,
            1,
            check_in + timedelta(days=5),
            check_out + timedelta(days=5),
        )
        self.assertIsNone(r2)

    def test_cancel_reservation(self):
        """cancel_reservation marca cancelada y libera habitación."""
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        r = self.reservation_svc.create_reservation(
            self.customer.id, self.hotel.id, 2, check_in, check_out
        )
        self.assertTrue(self.reservation_svc.cancel_reservation(r.id))
        hotel = self.hotel_svc.get_hotel(self.hotel.id)
        self.assertNotIn(2, hotel.reserved_rooms)
        self.assertFalse(self.reservation_svc.cancel_reservation("no-existe"))

    def test_create_reservation_room_out_of_range(self):
        """create_reservation retorna None si room_number fuera de rango."""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        self.assertIsNone(
            self.reservation_svc.create_reservation(
                self.customer.id, self.hotel.id, 0, check_in, check_out
            )
        )
        self.assertIsNone(
            self.reservation_svc.create_reservation(
                self.customer.id, self.hotel.id, 99, check_in, check_out
            )
        )
