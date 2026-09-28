import json
from pathlib import Path


ORDERS_FILE = Path("data/orders.json")


def get_order_status(order_id):
    """Return order status and expected delivery date."""

    with open(ORDERS_FILE, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:
        if str(order["order_id"]) == str(order_id):
            return {
                "status": order["status"],
                "expected_delivery_date": order["expected_delivery_date"]
            }

    return "order not found"
