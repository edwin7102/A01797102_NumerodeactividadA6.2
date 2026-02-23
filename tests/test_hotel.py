"""Tests para Hotel y HotelService."""

import tempfile
import unittest
from pathlib import Path

from models.hotel import Hotel
from services.hotel_service import HotelService
from storage.manager import StorageManager


class TestHotelModel(unittest.TestCase):
    """Tests del modelo Hotel."""

    def test_hotel_creation(self):
        """Hotel se crea con atributos correctos."""
        h = Hotel(
            id="h1",
            name="Madrid",
            address="Calle Principal 1",
            total_rooms=10,
            reserved_rooms=set(),
        )
        self.assertEqual(h.id, "h1")
        self.assertEqual(h.name, "Madrid")
        self.assertEqual(h.total_rooms, 10)
        self.assertEqual(h.available_rooms, 10)

    def test_hotel_available_rooms(self):
        """available_rooms es total menos reservadas."""
        h = Hotel(
            id="h1",
            name="Barcelona",
            address="Addr",
            total_rooms=5,
            reserved_rooms={1, 2},
        )
        self.assertEqual(h.available_rooms, 3)

    def test_hotel_to_dict_from_dict(self):
        """to_dict y from_dict son inversos."""
        h = Hotel(
            id="h1",
            name="París",
            address="Addr",
            total_rooms=5,
            reserved_rooms={1},
        )
        h2 = Hotel.from_dict(h.to_dict())
        self.assertEqual(h.id, h2.id)
        self.assertEqual(h.reserved_rooms, h2.reserved_rooms)


class TestHotelService(unittest.TestCase):
    """Tests de HotelService con persistencia."""

    def setUp(self):
        """Directorio temporal por test."""
        self.tmpdir = tempfile.mkdtemp()
        self.storage = StorageManager(Path(self.tmpdir))
        self.service = HotelService(self.storage)

    def test_create_hotel(self):
        """create_hotel crea y persiste."""
        h = self.service.create_hotel("Londres", "Dirección 1", 20)
        self.assertIsNotNone(h.id)
        self.assertEqual(h.name, "Londres")
        self.assertEqual(h.total_rooms, 20)
        self.assertEqual(len(self.storage.load_hotels()), 1)

    def test_delete_hotel(self):
        """delete_hotel elimina del almacenamiento."""
        h = self.service.create_hotel("Roma", "Addr", 5)
        self.assertTrue(self.service.delete_hotel(h.id))
        self.assertIsNone(self.service.get_hotel(h.id))
        self.assertFalse(self.service.delete_hotel("inexistente"))

    def test_display_hotel(self):
        """display_hotel retorna información formateada."""
        h = self.service.create_hotel("Amsterdam", "Calle 1", 10)
        info = self.service.display_hotel(h.id)
        self.assertIn("Amsterdam", info)
        self.assertIn("Calle 1", info)
        self.assertIn("10", info)
        self.assertIsNone(self.service.display_hotel("no-existe"))

    def test_update_hotel(self):
        """update_hotel modifica campos."""
        h = self.service.create_hotel("Lisboa", "Addr", 5)
        updated = self.service.update_hotel(h.id, name="Lisboa Centro")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Lisboa Centro")
        self.assertEqual(updated.address, "Addr")

    def test_reserve_room(self):
        """reserve_room marca habitación como reservada."""
        h = self.service.create_hotel("Berlín", "Addr", 5)
        self.assertTrue(self.service.reserve_room(h.id, 1))
        self.assertTrue(self.service.reserve_room(h.id, 2))
        self.assertFalse(self.service.reserve_room(h.id, 1))
        self.assertFalse(self.service.reserve_room(h.id, 99))
        hotel = self.service.get_hotel(h.id)
        self.assertEqual(hotel.available_rooms, 3)

    def test_cancel_reservation(self):
        """cancel_reservation libera habitación."""
        h = self.service.create_hotel("Venecia", "Addr", 5)
        self.service.reserve_room(h.id, 1)
        self.assertTrue(self.service.cancel_reservation(h.id, 1))
        hotel = self.service.get_hotel(h.id)
        self.assertEqual(hotel.available_rooms, 5)
        self.assertFalse(self.service.cancel_reservation(h.id, 1))

    def test_reserve_room_hotel_not_found(self):
        """reserve_room retorna False si hotel no existe."""
        self.assertFalse(self.service.reserve_room("id-inexistente", 1))

    def test_cancel_reservation_hotel_not_found(self):
        """cancel_reservation retorna False si hotel no existe."""
        h = self.service.create_hotel("Tokio", "A", 5)
        self.assertFalse(self.service.cancel_reservation("id-inexistente", 1))

    def test_update_hotel_not_found(self):
        """update_hotel retorna None si hotel no existe."""
        self.assertIsNone(
            self.service.update_hotel("no-existe", name="Milán")
        )

    def test_get_hotel_not_found(self):
        """get_hotel retorna None si hotel no existe."""
        self.assertIsNone(self.service.get_hotel("no-existe"))

    def test_hotel_post_init_reserved_rooms_none(self):
        """Hotel con reserved_rooms=None inicializa como set vacío."""
        h = Hotel(
            id="h1", name="Milán", address="A", total_rooms=5, reserved_rooms=None
        )
        self.assertEqual(h.reserved_rooms, set())
        self.assertEqual(h.available_rooms, 5)
