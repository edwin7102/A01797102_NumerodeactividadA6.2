"""Almacenamiento en archivos JSON."""

import json
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


class StorageManager:
    """Lectura y escritura de datos."""

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._hotels_path = self.data_dir / "hotels.json"
        self._customers_path = self.data_dir / "customers.json"
        self._reservations_path = self.data_dir / "reservations.json"

    def _read_json(self, path):
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []

    def _write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_hotels(self):
        return self._read_json(self._hotels_path)

    def save_hotels(self, hotels):
        self._write_json(self._hotels_path, hotels)

    def load_customers(self):
        return self._read_json(self._customers_path)

    def save_customers(self, customers):
        self._write_json(self._customers_path, customers)

    def load_reservations(self):
        return self._read_json(self._reservations_path)

    def save_reservations(self, reservations):
        self._write_json(self._reservations_path, reservations)
