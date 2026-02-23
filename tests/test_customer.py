"""Tests para Customer."""

import tempfile
import unittest
from pathlib import Path

from models.customer import Customer
from services.customer_service import CustomerService
from storage.manager import StorageManager


class TestCustomerModel(unittest.TestCase):
    """Tests del modelo Customer."""

    def test_customer_creation(self):
        """Customer se crea con atributos correctos."""
        c = Customer(
            id="c1",
            name="Lionel Messi",
            email="messi@tecmna.com",
            phone="+52 123 123 1234",
        )
        self.assertEqual(c.id, "c1")
        self.assertEqual(c.name, "Lionel Messi")
        self.assertEqual(c.email, "messi@tecmna.com")

    def test_customer_to_dict_from_dict(self):
        """to_dict y from_dict son inversos."""
        c = Customer(id="c1", name="Kylian Mbappé", email="mbappe@tecmna.com",
                     phone="123")
        c2 = Customer.from_dict(c.to_dict())
        self.assertEqual(c.id, c2.id)
        self.assertEqual(c.name, c2.name)


class TestCustomerService(unittest.TestCase):
    """Tests de CustomerService."""

    def setUp(self):
        """Directorio temporal."""
        self.tmpdir = tempfile.mkdtemp()
        self.storage = StorageManager(Path(self.tmpdir))
        self.service = CustomerService(self.storage)

    def test_create_customer(self):
        """create_customer crea un cliente."""
        c = self.service.create_customer("Cristiano Ronaldo", "ronaldo@tecmna.com")
        self.assertIsNotNone(c.id)
        self.assertEqual(c.name, "Cristiano Ronaldo")
        self.assertEqual(len(self.storage.load_customers()), 1)

    def test_delete_customer(self):
        """delete_customer elimina un cliente."""
        c = self.service.create_customer("Neymar Jr", "neymar@tecmna.com")
        self.assertTrue(self.service.delete_customer(c.id))
        self.assertIsNone(self.service.get_customer(c.id))
        self.assertFalse(self.service.delete_customer("inexistente"))

    def test_display_customer(self):
        """display_customer retorna información formateada."""
        c = self.service.create_customer("Erling Haaland", "haaland@tecmna.com")
        info = self.service.display_customer(c.id)
        self.assertIn("Erling Haaland", info)
        self.assertIn("haaland@tecmna.com", info)
        self.assertIsNone(self.service.display_customer("no-existe"))

    def test_update_customer(self):
        """update_customer modifica campos."""
        c = self.service.create_customer("Karim Benzema", "benzema@tecmna.com")
        updated = self.service.update_customer(
            c.id, name="Robert Lewandowski", email="lewandowski@tecmna.com"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Robert Lewandowski")
        self.assertEqual(updated.email, "lewandowski@tecmna.com")

    def test_update_customer_not_found(self):
        """update_customer retorna None si cliente no existe."""
        self.assertIsNone(
            self.service.update_customer("no-existe", name="Nuevo")
        )

    def test_display_customer_phone_empty(self):
        """display_customer muestra 'No especificado' si phone vacío."""
        c = self.service.create_customer("Mohamed Salah", "salah@tecmna.com",
                                         phone="")
        info = self.service.display_customer(c.id)
        self.assertIn("No especificado", info)

    def test_service_with_default_storage(self):
        """CustomerService funciona con StorageManager por defecto."""
        svc = CustomerService()
        c = svc.create_customer("Luka Modric", "modric@tecmna.com")
        self.assertIsNotNone(c.id)
        self.assertEqual(c.name, "Luka Modric")
