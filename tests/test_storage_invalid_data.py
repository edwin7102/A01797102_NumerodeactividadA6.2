"""Tests para manejo de datos inválidos en archivos."""

import tempfile
import unittest
from io import StringIO
import sys
from pathlib import Path

from services.hotel_service import HotelService
from storage.manager import StorageManager


class TestInvalidFileData(unittest.TestCase):
    """Verifica que datos inválidos se manejen sin interrumpir ejecución."""

    def setUp(self):
        """Captura stderr para inspeccionar mensajes de error."""
        self.tmpdir = tempfile.mkdtemp()
        self.storage = StorageManager(Path(self.tmpdir))
        self._stderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        """Restaura stderr."""
        sys.stderr = self._stderr

    def _stderr_content(self):
        return sys.stderr.getvalue()

    def test_validacion_1_json_corrupto(self):
        """Caso 1: JSON con sintaxis inválida - retorna [] y mensaje."""
        self.storage._hotels_path.write_text("{ invalid json }")
        result = self.storage.load_hotels()
        self.assertEqual(result, [])
        self.assertIn("[ERROR]", self._stderr_content())
        self.assertIn("JSON inválido", self._stderr_content())

    def test_validacion_2_hotel_campos_faltantes(self):
        """Caso 2: Hotel con campos obligatorios faltantes - se omite."""
        self.storage._hotels_path.write_text("""[
            {"id": "h1", "name": "Madrid", "address": "Addr", "total_rooms": 5,
             "reserved_rooms": []},
            {"id": "h2", "name": "Bad"},
            {"id": "h3", "name": "Barcelona", "address": "A2", "total_rooms": 3,
             "reserved_rooms": []}
        ]""")
        result = self.storage.load_hotels()
        self.assertEqual(len(result), 2)
        self.assertIn("Hotel registro inválido", self._stderr_content())
        self.assertIn("Registros inválidos omitidos: 1 en Hotel",
                      self._stderr_content())

    def test_validacion_3_hotel_tipo_incorrecto(self):
        """Caso 3: Hotel con reserved_rooms tipo incorrecto (int) - se omite."""
        self.storage._hotels_path.write_text("""[
            {"id": "h1", "name": "París", "address": "A", "total_rooms": 5,
             "reserved_rooms": 99}
        ]""")
        result = self.storage.load_hotels()
        self.assertEqual(len(result), 0)
        self.assertIn("Hotel registro inválido", self._stderr_content())

    def test_validacion_4_cliente_estructura_incorrecta(self):
        """Caso 4: Cliente con estructura/datos inválidos - se omite."""
        self.storage._customers_path.write_text("""[
            {"id": "c1", "name": "Kylian Mbappé", "email": "mbappe@tecmna.com"},
            {"wrong": "structure", "no_email": true},
            {"id": "c2", "name": "SinEmail"}
        ]""")
        result = self.storage.load_customers()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Kylian Mbappé")
        self.assertIn("Cliente registro inválido", self._stderr_content())
        self.assertIn("Registros inválidos omitidos", self._stderr_content())

    def test_validacion_5_reservacion_fecha_invalida(self):
        """Caso 5: Reservación con fecha en formato inválido - se omite."""
        self.storage._reservations_path.write_text("""[
            {"id": "r1", "customer_id": "c1", "hotel_id": "h1",
             "room_number": 1, "check_in": "2025-01-01",
             "check_out": "2025-01-05", "status": "active"},
            {"id": "r2", "customer_id": "c2", "hotel_id": "h2",
             "room_number": 1, "check_in": "not-a-date",
             "check_out": "2025-01-05", "status": "active"}
        ]""")
        result = self.storage.load_reservations()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "r1")
        self.assertIn("Reservación registro inválido", self._stderr_content())

    def test_validacion_6_registro_no_diccionario(self):
        """Caso 6: Registro que no es diccionario - se omite."""
        self.storage._customers_path.write_text("""[
            {"id": "c1", "name": "Lionel Messi", "email": "messi@tecmna.com"},
            ["lista", "en", "vez", "de", "dict"],
            {"id": "c2", "name": "Cristiano Ronaldo", "email": "ronaldo@tecmna.com"}
        ]""")
        result = self.storage.load_customers()
        self.assertEqual(len(result), 2)
        self.assertIn("no es diccionario", self._stderr_content())

    def test_validacion_7_json_dict_not_list(self):
        """Caso 7: JSON válido pero es objeto no lista - retorna []."""
        self.storage._hotels_path.write_text('{"key": "value"}')
        result = self.storage.load_hotels()
        self.assertEqual(result, [])

    def test_servicio_continua_con_invalidos(self):
        """Los servicios operan correctamente con datos parcialmente inválidos."""
        self.storage._hotels_path.write_text("""[
            {"id": "bad"},
            {"id": "h1", "name": "Lisboa", "address": "A", "total_rooms": 5,
             "reserved_rooms": []}
        ]""")
        hs = HotelService(self.storage)
        hotel = hs.get_hotel("h1")
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name, "Lisboa")
        info = hs.display_hotel("h1")
        self.assertIn("Lisboa", info)
