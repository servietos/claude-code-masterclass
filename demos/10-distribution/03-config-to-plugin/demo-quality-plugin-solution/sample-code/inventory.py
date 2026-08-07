from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    unit_price: Decimal
    on_hand: int


class InventoryError(Exception):
    pass


class Inventory:
    def __init__(self, items: Iterable[Item] = ()):
        self._items: dict[str, Item] = {item.sku: item for item in items}

    def add(self, item: Item) -> None:
        if item.sku in self._items:
            raise InventoryError(f"duplicate sku: {item.sku}")
        self._items[item.sku] = item

    def adjust(self, sku: str, delta: int) -> Item:
        current = self._items.get(sku)
        if current is None:
            raise InventoryError(f"unknown sku: {sku}")
        new_count = current.on_hand + delta
        if new_count < 0:
            raise InventoryError(f"cannot drop below zero for sku: {sku}")
        updated = Item(current.sku, current.name, current.unit_price, new_count)
        self._items[sku] = updated
        return updated

    def value(self) -> Decimal:
        return sum(
            (item.unit_price * item.on_hand for item in self._items.values()),
            start=Decimal(0),
        )

    def low_stock(self, threshold: int) -> list[Item]:
        return [item for item in self._items.values() if item.on_hand <= threshold]
