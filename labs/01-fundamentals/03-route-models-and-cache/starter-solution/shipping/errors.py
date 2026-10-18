class ShippingError(Exception):
    pass


class UnknownCountry(ShippingError):
    pass


class EmptyQuote(ShippingError):
    pass
