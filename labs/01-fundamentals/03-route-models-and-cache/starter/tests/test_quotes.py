import unittest

from shipping.errors import EmptyQuote, UnknownCountry
from shipping.parcels import Parcel
from shipping.quotes import quote_cents
from shipping.rates import parcel_price_cents


class RateTests(unittest.TestCase):
    def test_whole_kilo_in_zone_one(self):
        self.assertEqual(parcel_price_cents(2000, "AT"), 495 + 2 * 120)

    def test_unknown_country(self):
        with self.assertRaises(UnknownCountry):
            parcel_price_cents(1000, "XX")


class QuoteTests(unittest.TestCase):
    def test_single_parcel_includes_surcharge(self):
        parcel = Parcel(weight_g=3000, length_cm=10, width_cm=10, height_cm=10)
        subtotal = 495 + 3 * 120
        self.assertEqual(quote_cents([parcel], "DE"), subtotal + subtotal * 8 // 100)

    def test_empty_quote(self):
        with self.assertRaises(EmptyQuote):
            quote_cents([], "DE")


if __name__ == "__main__":
    unittest.main()
