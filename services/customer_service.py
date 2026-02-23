"""Servicio de clientes: Create, Delete, Display, Update."""

import uuid
from models.customer import Customer
from storage.manager import StorageManager


class CustomerService:
    """Servicio para gestión de clientes."""

    def __init__(self, storage=None):
        self.storage = storage or StorageManager()

    def create_customer(self, name, email, phone=""):
        """Create"""
        customer_id = str(uuid.uuid4())
        customer = Customer(id=customer_id, name=name, email=email, phone=phone)
        customers = self.storage.load_customers()
        customers.append(customer.to_dict())
        self.storage.save_customers(customers)
        return customer

    def delete_customer(self, customer_id):
        """Delete"""
        customers = self.storage.load_customers()
        original = len(customers)
        customers = [c for c in customers if c["id"] != customer_id]
        if len(customers) < original:
            self.storage.save_customers(customers)
            return True
        return False

    def display_customer(self, customer_id):
        """Get by id"""
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        lines = [
            f"Cliente: {customer.name}",
            f"  ID: {customer.id}",
            f"  Email: {customer.email}",
            f"  Teléfono: {customer.phone or 'No especificado'}",
        ]
        return "\n".join(lines)

    def update_customer(self, customer_id, name=None, email=None, phone=None):
        """Update"""
        customers = self.storage.load_customers()
        for i, c in enumerate(customers):
            if c["id"] == customer_id:
                if name is not None:
                    customers[i]["name"] = name
                if email is not None:
                    customers[i]["email"] = email
                if phone is not None:
                    customers[i]["phone"] = phone
                self.storage.save_customers(customers)
                return Customer.from_dict(customers[i])
        return None

    def get_customer(self, customer_id):
        """Obtiene un cliente por ID."""
        customers = self.storage.load_customers()
        for c in customers:
            if c["id"] == customer_id:
                return Customer.from_dict(c)
        return None
