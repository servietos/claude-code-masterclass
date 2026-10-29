import json
import sys

from inventory import low_stock
from orders import place_order

if __name__ == "__main__":
    order = place_order({"espresso-beans": 2, "filter-papers": 1}, years_as_customer=4)
    json.dump({"order": order, "low_stock": low_stock()}, sys.stdout, indent=2)
