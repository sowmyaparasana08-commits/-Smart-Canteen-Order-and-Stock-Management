def process_canteen_orders(menu_inventory, orders, tax_rate=0.05):
    """
    Processes successive customer orders, updates stock, rejects unavailable items/quantities,
    and generates a daily sales and remaining inventory summary.

    menu_inventory format:
    {
        "ITEM_CODE": {"name": "Item Name", "price": 50.0, "stock": 20}
    }

    orders format: list of dicts
    {
        "order_id": "ORD-001",
        "customer": "Student Name",
        "items": [("ITEM_CODE", qty), ...]
    }
    """
    # Copy inventory so original input dictionary is not mutated unexpectedly
    stock_state = {}
    for code, details in menu_inventory.items():
        stock_state[code] = {
            "name": details["name"],
            "price": float(details["price"]),
            "initial_stock": int(details["stock"]),
            "remaining_stock": int(details["stock"]),
            "units_sold": 0,
            "revenue": 0.0,
        }

    order_receipts = []
    total_gross_sales = 0.0
    total_tax_collected = 0.0
    total_net_revenue = 0.0
    accepted_orders = 0
    partially_fulfilled_orders = 0
    rejected_orders = 0

    print("=" * 76)
    print("SMART CANTEEN ORDER & STOCK MANAGEMENT SYSTEM")
    print("=" * 76)

    for idx, order in enumerate(orders, start=1):
        order_id = order.get("order_id", f"ORD-{idx:03d}")
        customer = order.get("customer", "Walk-in Customer")
        requested_items = order.get("items", [])

        fulfilled_lines = []
        rejected_lines = []
        subtotal = 0.0

        for code, qty in requested_items:
            item_code = str(code).strip().upper()

            if item_code not in stock_state:
                rejected_lines.append(f"Item '{item_code}' (qty {qty}): Not found on canteen menu")
                continue

            item = stock_state[item_code]

            if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                rejected_lines.append(f"{item['name']} (qty {qty}): Quantity must be a positive integer")
                continue

            if qty > item["remaining_stock"]:
                rejected_lines.append(
                    f"{item['name']} (requested {qty}): Insufficient stock "
                    f"(available: {item['remaining_stock']})"
                )
                continue

            # Valid item and sufficient stock -> deduct inventory and add to bill
            line_total = round(item["price"] * qty, 2)
            item["remaining_stock"] -= qty
            item["units_sold"] += qty
            item["revenue"] = round(item["revenue"] + line_total, 2)
            subtotal = round(subtotal + line_total, 2)

            fulfilled_lines.append({
                "code": item_code,
                "name": item["name"],
                "qty": qty,
                "unit_price": item["price"],
                "line_total": line_total,
            })

        tax_amount = round(subtotal * tax_rate, 2)
        net_bill = round(subtotal + tax_amount, 2)

        if fulfilled_lines and not rejected_lines:
            status = "ACCEPTED"
            accepted_orders += 1
        elif fulfilled_lines and rejected_lines:
            status = "PARTIAL"
            partially_fulfilled_orders += 1
        else:
            status = "REJECTED"
            rejected_orders += 1

        total_gross_sales = round(total_gross_sales + subtotal, 2)
        total_tax_collected = round(total_tax_collected + tax_amount, 2)
        total_net_revenue = round(total_net_revenue + net_bill, 2)

        order_receipts.append({
            "order_id": order_id,
            "customer": customer,
            "status": status,
            "fulfilled": fulfilled_lines,
            "rejected": rejected_lines,
            "subtotal": subtotal,
            "tax": tax_amount,
            "total": net_bill,
        })

        # Print Order Receipt
        print(f"\nOrder {order_id} | Customer: {customer} | Status: {status}")
        print("-" * 76)
        if fulfilled_lines:
            for line in fulfilled_lines:
                print(
                    f"  [BILLED]   {line['name']:<20} x {line['qty']:<3} @ "
                    f"{line['unit_price']:>6.2f} = {line['line_total']:>7.2f}"
                )
        if rejected_lines:
            for rej in rejected_lines:
                print(f"  [REJECTED] {rej}")
        print(
            f"  Subtotal: {subtotal:>7.2f} | Tax ({tax_rate * 100:.0f}%): "
            f"{tax_amount:>6.2f} | Net Bill: {net_bill:>7.2f}"
        )

    # Daily Sales Summary
    print("\n" + "=" * 76)
    print("DAILY SALES SUMMARY")
    print("=" * 76)
    print(f"Total Orders Processed : {len(orders)}")
    print(f"  - Fully Accepted     : {accepted_orders}")
    print(f"  - Partially Fulfilled: {partially_fulfilled_orders}")
    print(f"  - Completely Rejected: {rejected_orders}")
    print(f"Gross Item Sales       : {total_gross_sales:.2f}")
    print(f"Total Tax Collected    : {total_tax_collected:.2f}")
    print(f"Total Net Revenue      : {total_net_revenue:.2f}")

    # Remaining Inventory Summary
    print("\n" + "=" * 76)
    print("REMAINING STOCK & ITEM SALES SUMMARY")
    print("=" * 76)
    print(f"{'Code':<8} | {'Item Name':<20} | {'Init':>5} | {'Sold':>5} | {'Rem':>5} | {'Sales':>8}")
    print("-" * 76)
    for code, st in stock_state.items():
        print(
            f"{code:<8} | {st['name']:<20} | {st['initial_stock']:>5} | "
            f"{st['units_sold']:>5} | {st['remaining_stock']:>5} | {st['revenue']:>8.2f}"
        )
    print("=" * 76)

    return {
        "receipts": order_receipts,
        "inventory": stock_state,
        "total_net_revenue": total_net_revenue,
    }


if __name__ == "__main__":
    canteen_menu = {
        "SAM": {"name": "Veg Samosa", "price": 15.0, "stock": 25},
        "DOS": {"name": "Masala Dosa", "price": 55.0, "stock": 12},
        "COF": {"name": "Filter Coffee", "price": 20.0, "stock": 30},
        "JUC": {"name": "Fresh Lime Juice", "price": 25.0, "stock": 8},
        "SAND": {"name": "Grilled Sandwich", "price": 45.0, "stock": 10},
    }

    customer_orders = [
        {
            "order_id": "ORD-101",
            "customer": "Arjun Rao",
            "items": [("SAM", 3), ("COF", 2)],
        },
        {
            "order_id": "ORD-102",
            "customer": "Sneha Patel",
            "items": [("DOS", 4), ("JUC", 10)],  # JUC exceeds stock (8 available)
        },
        {
            "order_id": "ORD-103",
            "customer": "Vikram Nair",
            "items": [("JUC", 8), ("SAND", 2)],
        },
        {
            "order_id": "ORD-104",
            "customer": "Pooja Sharma",
            "items": [("BURGER", 1), ("SAM", -2)],  # Invalid item & negative quantity
        },
        {
            "order_id": "ORD-105",
            "customer": "Rahul Verma",
            "items": [("DOS", 8), ("COF", 5)],
        },
    ]

    process_canteen_orders(canteen_menu, customer_orders, tax_rate=0.05)
