"""
Задача 17: Система скидок.
ООП-стиль
"""

from dataclasses import dataclass, field

@dataclass
class OrderItem:
    """Позиция заказа: товар с ценой и количеством."""
    name: str
    price: float
    qty: int = 1

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if self.qty <= 0:
            raise ValueError("Количество должно быть > 0")

    @property
    def total(self) -> float:
        return self.price * self.qty


@dataclass
class Coupon:
    """Купон: код и процент скидки."""
    code: str
    percent: float

    def __post_init__(self):
        if not (0 <= self.percent <= 100):
            raise ValueError("Процент купона должен быть от 0 до 100")

    def discount_for(self, amount: float) -> float:
        return amount * self.percent / 100.0


class DiscountPolicy:
    """
    Политика скидок от суммы чека.
    Инкапсулирует порог и процент — их можно менять независимо от заказа.
    """
    def __init__(self, threshold: float = 100.0, percent: float = 5.0):
        if threshold < 0 or not (0 <= percent <= 100):
            raise ValueError("Некорректные параметры политики скидок")
        self.threshold = threshold
        self.percent = percent

    def discount_for(self, amount: float) -> float:
        if amount >= self.threshold:
            return amount * self.percent / 100.0
        return 0.0

class Order:
    """
    Заказ: хранит позиции, купон и политику скидок.
    Сам умеет добавлять/удалять позиции и считать итог.
    """
    def __init__(self, policy: DiscountPolicy | None = None):
        self._items: list[OrderItem] = []
        self._coupon: Coupon | None = None
        self._policy = policy or DiscountPolicy()

    # --- позиции ---
    def add_item(self, name: str, price: float, qty: int = 1) -> None:
        for item in self._items:
            if item.name == name:
                item.qty += qty
                return
        self._items.append(OrderItem(name, float(price), int(qty)))

    def remove_item(self, name: str) -> bool:
        for i, item in enumerate(self._items):
            if item.name == name:
                self._items.pop(i)
                return True
        return False

    def change_qty(self, name: str, qty: int) -> bool:
        for item in self._items:
            if item.name == name:
                if qty <= 0:
                    self._items.remove(item)
                else:
                    item.qty = int(qty)
                return True
        return False

    def apply_coupon(self, coupon: Coupon) -> None:
        self._coupon = coupon

    def clear_coupon(self) -> None:
        self._coupon = None

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self._items)

    def _coupon_discount(self, amount: float) -> float:
        return self._coupon.discount_for(amount) if self._coupon else 0.0

    def totals(self) -> dict:
        """Возвращает словарь с разбивкой итога."""
        s = self.subtotal
        coupon_disc = self._coupon_discount(s)
        after_coupon = s - coupon_disc
        bulk_disc = self._policy.discount_for(after_coupon)
        return {
            "subtotal": s,
            "coupon_discount": coupon_disc,
            "bulk_discount": bulk_disc,
            "total": after_coupon - bulk_disc,
        }

    def print_receipt(self, title: str = "Чек") -> None:
        print(f"\n=== {title} ===")
        if not self._items:
            print("  (заказ пуст)")
        for item in self._items:
            print(f"  {item.name:<12} {item.price:>8.2f} x {item.qty:<3} = {item.total:>10.2f}")
        t = self.totals()
        print(f"  {'Подытог:':<30} {t['subtotal']:>10.2f}")
        if self._coupon:
            print(f"  Купон {self._coupon.code} (-{self._coupon.percent:.1f}%):"
                  f"{'':<15} -{t['coupon_discount']:>9.2f}")
        if t["bulk_discount"] > 0:
            print(f"  Скидка от суммы (-{self._policy.percent:.1f}%):"
                  f"{'':<12} -{t['bulk_discount']:>9.2f}")
        print(f"  {'ИТОГО:':<30} {t['total']:>10.2f}")


if __name__ == "__main__":
    policy = DiscountPolicy(threshold=100.0, percent=5.0)


    order = Order(policy)
    order.add_item("Хлеб", 2.5, 2)
    order.add_item("Молоко", 3.2, 1)
    order.print_receipt("Демо 1: без купона, сумма < порога")


    order.add_item("Сыр", 25.0, 4)
    order.print_receipt("Демо 2: сумма >= порога, скидка от чека")


    order.apply_coupon(Coupon("SALE10", 10))
    order.print_receipt("Демо 3: купон SALE10 (-10%) + скидка от суммы")


    order.change_qty("Хлеб", 5)
    order.remove_item("Молоко")
    order.print_receipt("Демо 4: изменили кол-во хлеба, убрали молоко")

    order.clear_coupon()
    order.print_receipt("Демо 5: купон снят")

    print("\n--- Демонстрация смены политики скидок ---")
    strict_policy = DiscountPolicy(threshold=50.0, percent=10.0)
    order2 = Order(strict_policy)
    order2.add_item("Книга", 30.0, 2)   # 60 >= 50 → 10%
    order2.apply_coupon(Coupon("STUDENT", 15))
    order2.print_receipt("Демо 6: порог 50, скидка 10% + купон 15%")
