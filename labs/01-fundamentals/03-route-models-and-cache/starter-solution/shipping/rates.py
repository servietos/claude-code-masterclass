from shipping.zones import zone_for

BASE_CENTS = {1: 495, 2: 725, 3: 1190}
PER_KG_CENTS = {1: 120, 2: 210, 3: 380}


def billable_kg(weight_g: int) -> int:
    return weight_g // 1000


def parcel_price_cents(weight_g: int, country: str) -> int:
    zone = zone_for(country)
    return BASE_CENTS[zone] + billable_kg(weight_g) * PER_KG_CENTS[zone]
