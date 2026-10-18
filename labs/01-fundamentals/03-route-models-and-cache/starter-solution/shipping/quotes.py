from shipping.errors import EmptyQuote
from shipping.parcels import Parcel, chargeable_weight_g
from shipping.rates import parcel_price_cents

FUEL_SURCHARGE_PERCENT = 8


def quote_cents(parcels: list[Parcel], country: str) -> int:
    if not parcels:
        raise EmptyQuote(country)
    subtotal = sum(
        parcel_price_cents(chargeable_weight_g(p), country) for p in parcels
    )
    surcharge = subtotal * FUEL_SURCHARGE_PERCENT // 100
    return subtotal + surcharge


def format_quote(parcels: list[Parcel], country: str) -> str:
    total = quote_cents(parcels, country)
    return f"{len(parcels)} parcel(s) to {country.upper()}: {total / 100:.2f} EUR"
