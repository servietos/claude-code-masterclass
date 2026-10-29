import pytest

from inventory import add_item, connect, find_by_sku, low_stock, restock


@pytest.fixture
def db():
    db = connect()
    add_item(db, "A-100", "Cable", 12, 5)
    add_item(db, "B-200", "Adapter", 4, 4)
    return db


def test_find_by_sku_treats_the_sku_as_data(db):
    assert find_by_sku(db, "X' OR '1'='1") is None


def test_restock_rejects_a_negative_amount(db):
    with pytest.raises(ValueError):
        restock(db, "A-100", -5)


def test_low_stock_includes_items_at_their_reorder_level(db):
    assert low_stock(db) == ["B-200"]
