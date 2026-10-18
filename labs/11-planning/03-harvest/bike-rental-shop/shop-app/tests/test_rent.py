import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import rentals


class RentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db.DB_PATH = Path(self.tmp.name) / "test.db"
        db.init_db()
        rentals.add_bike("CITY-01", "M")

    def tearDown(self):
        self.tmp.cleanup()

    def test_rent_marks_bike_rented(self):
        rentals.rent_bike("CITY-01", "Ana", "0660111", 2)
        self.assertEqual(len(rentals.list_open()), 1)

    def test_rent_twice_fails(self):
        rentals.rent_bike("CITY-01", "Ana", "0660111", 2)
        with self.assertRaises(ValueError):
            rentals.rent_bike("CITY-01", "Ben", "0660222", 1)


if __name__ == "__main__":
    unittest.main()
