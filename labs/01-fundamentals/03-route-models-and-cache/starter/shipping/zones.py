from shipping.errors import UnknownCountry

ZONES = {
    "AT": 1,
    "DE": 1,
    "CZ": 1,
    "FR": 2,
    "IT": 2,
    "ES": 2,
    "NL": 2,
    "US": 3,
    "CA": 3,
    "JP": 3,
}


def zone_for(country: str) -> int:
    try:
        return ZONES[country.upper()]
    except KeyError:
        raise UnknownCountry(country)
