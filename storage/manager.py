"""Almacenamiento en archivos JSON."""

import json
import sys
from pathlib import Path

from models.customer import Customer
from models.hotel import Hotel
from models.reservation import Reservation

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


def _log_error(msg):
    """Muestra errores en consola. La ejecución continúa."""
    print(f"[ERROR] {msg}", file=sys.stderr)


class StorageManager:
    """Lectura y escritura de datos."""

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._hotels_path = self.data_dir / "hotels.json"
        self._customers_path = self.data_dir / "customers.json"
        self._reservations_path = self.data_dir / "reservations.json"

    def _read_json(self, path):
        """Lee JSON. Ante error, imprime en consola."""
        if not path.exists():
            return []
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            _log_error(f"JSON inválido en {path}: {e}")
            return []
        except OSError as e:
            _log_error(f"No se pudo leer {path}: {e}")
            return []

    def _write_json(self, path, data):
        """Escribe datos. Ante error, imprime en consola y continúa."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            _log_error(f"No se pudo escribir {path}: {e}")

    def _filter_valid_records(self, records, model_class, entity_name):
        """Filtra registros válidos. Registros inválidos se omiten con mensaje."""
        valid = []
        invalid_count = 0
        for i, rec in enumerate(records):
            if not isinstance(rec, dict):
                _log_error(f"{entity_name} registro {i}: no es diccionario")
                invalid_count += 1
                continue
            try:
                model_class.from_dict(rec)
                valid.append(rec)
            except (KeyError, TypeError, ValueError) as e:
                _log_error(f"{entity_name} registro inválido (índice {i}): {e}")
                invalid_count += 1
        if invalid_count > 0:
            _log_error(
                f"Registros inválidos omitidos: {invalid_count} en {entity_name}"
            )
        return valid

    def load_hotels(self):
        """Carga la lista de hoteles."""
        data = self._read_json(self._hotels_path)
        return self._filter_valid_records(data, Hotel, "Hotel")

    def save_hotels(self, hotels):
        """Guarda la lista de hoteles."""
        self._write_json(self._hotels_path, hotels)

    def load_customers(self):
        """Carga la lista de clientes."""
        data = self._read_json(self._customers_path)
        return self._filter_valid_records(data, Customer, "Cliente")

    def save_customers(self, customers):
        """Guarda la lista de clientes."""
        self._write_json(self._customers_path, customers)

    def load_reservations(self):
        """Carga la lista de reservaciones."""
        data = self._read_json(self._reservations_path)
        return self._filter_valid_records(data, Reservation, "Reservación")

    def save_reservations(self, reservations):
        """Guarda la lista de reservaciones."""
        self._write_json(self._reservations_path, reservations)
