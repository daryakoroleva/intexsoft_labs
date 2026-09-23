"""
Задача 17: Система скидок.
Структурный стиль: данные — словари/списки, логика — отдельные функции.
"""
order = []
coupon = None

BULK_THRESHOLD = 100.0 
BULK_PERCENT = 5.0      

def add_item(order, name, price, qty=1):
    """Добавить товар в заказ. Если такой уже есть — увеличить количество."""
    if price < 0 or qty <= 0:
        raise ValueError("Цена должна быть >= 0, количество > 0")
    for item in order:
        if item["name"] == name:
            item["qty"] += qty
            return
    order.append({"name": name, "price": float(price), "qty": int(qty)})


def remove_item(order, name):
    """Удалить позицию по названию."""
    for i, item in enumerate(order):
        if item["name"] == name:
            order.pop(i)
            return True
    return False


def change_qty(order, name, qty):
    """Изменить количество позиции. Если qty <= 0 — удалить."""
    for item in order:
        if item["name"] == name:
            if qty <= 0:
                order.remove(item)
            else:
                item["qty"] = int(qty)
            return True
    return False


def subtotal(order):
    """Сумма без скидок."""
    return sum(item["price"] * item["qty"] for item in order)


def apply_coupon(coupon, code, percent):
    """Применить купон: задать код и процент скидки."""
    if not (0 <= percent <= 100):
        raise ValueError("Процент скидки должен быть от 0 до 100")
    coupon["code"] = code
    coupon["percent"] = float(percent)


def clear_coupon(coupon):
    """Снять купон."""
    coupon["code"] = None
    coupon["percent"] = 0.0

def calc_coupon_discount(order, coupon):
    """Скидка по купону в денежном выражении."""
    if coupon["code"] is None:
        return 0.0
    return subtotal(order) * coupon["percent"] / 100.0


def calc_bulk_discount(order):
    """Скидка от суммы чека (если сумма >= порога)."""
    s = subtotal(order)
    if s >= BULK_THRESHOLD:
        return s * BULK_PERCENT / 100.0
    return 0.0


def calc_total(order, coupon):
    """
    Итог со скидками.
    Скидки применяются последовательно: сначала купон, потом от суммы.
    """
    s = subtotal(order)
    coupon_disc = calc_coupon_discount(order, coupon)
    after_coupon = s - coupon_disc
    bulk_disc = after_coupon * BULK_PERCENT / 100.0 if after_coupon >= BULK_THRESHOLD else 0.0
    return {
        "subtotal": s,
        "coupon_discount": coupon_disc,
        "bulk_discount": bulk_disc,
        "total": after_coupon - bulk_disc,
    }

def print_order(order, coupon, title):
    print(f"\n=== {title} ===")
    if not order:
        print("  (заказ пуст)")
    for item in order:
        print(f"  {item['name']:<12} {item['price']:>8.2f} x {item['qty']:<3} = {item['price']*item['qty']:>10.2f}")
    r = calc_total(order, coupon)
    print(f"  {'Подытог:':<30} {r['subtotal']:>10.2f}")
    if coupon["code"]:
        print(f"  Купон {coupon['code']} (-{coupon['percent']:.1f}%):{'':<15} -{r['coupon_discount']:>9.2f}")
    if r["bulk_discount"] > 0:
        print(f"  Скидка от суммы (-{BULK_PERCENT:.1f}%):{'':<12} -{r['bulk_discount']:>9.2f}")
    print(f"  {'ИТОГО:':<30} {r['total']:>10.2f}")


if __name__ == "__main__":
    coupon = {"code": None, "percent": 0.0}

    #обычный заказ без купона
    add_item(order, "Хлеб", 2.5, 2)
    add_item(order, "Молоко", 3.2, 1)
    print_order(order, coupon, "Демо 1: без купона, сумма < порога")

    #тот же заказ + дорогой товар - сработает скидка от суммы
    add_item(order, "Сыр", 25.0, 4)
    print_order(order, coupon, "Демо 2: сумма >= порога, скидка от чека")

    #применяем купон 10%
    apply_coupon(coupon, "SALE10", 10)
    print_order(order, coupon, "Демо 3: купон SALE10 (-10%) + скидка от суммы")

    #изменение количества и удаление
    change_qty(order, "Хлеб", 5)
    remove_item(order, "Молоко")
    print_order(order, coupon, "Демо 4: изменили кол-во хлеба, убрали молоко")

    clear_coupon(coupon)
    print_order(order, coupon, "Демо 5: купон снят")
