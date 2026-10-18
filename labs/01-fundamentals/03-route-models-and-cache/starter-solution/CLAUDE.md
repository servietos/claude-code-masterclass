# CLAUDE.md

## Architecture

Parcel shipping quotes for a small web shop, one module per concern in `shipping/`: `zones.py` maps a country to a zone, `rates.py` prices one parcel, `parcels.py` holds the parcel record and its volumetric weight, `quotes.py` combines parcels into a quote with a fuel surcharge. `quotes.py` imports the other three; nothing imports `quotes.py`.

## Conventions

Money is an integer number of cents, never a float. Weights are integer grams. Public functions have type hints and raise `ShippingError` subclasses, never bare `ValueError`.

## Testing

Tests use the standard library only: `python -m unittest discover -s tests`. Do not add a dependency.

## Workflow

Keep diffs minimal and touch only the files a task names. This sample exists to be read and measured, not refactored.
