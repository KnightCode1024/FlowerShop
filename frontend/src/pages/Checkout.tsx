import { useMemo, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { formatPrice } from "../api/catalogApi";
import { createInvoice, updateCart, type DeliveryAddress } from "../api/orderApi";
import { ApiError } from "../api/authApi";
import { useCart } from "../cart/useCart";

export default function Checkout() {
  const { items, totalAmount } = useCart();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [deliveryAddress, setDeliveryAddress] = useState<DeliveryAddress>({
    recipient_name: "",
    recipient_phone: "",
    delivery_address: "",
    delivery_city: "",
    delivery_zip: "",
    delivery_notes: "",
  });

  const availabilityError = useMemo(() => {
    for (const item of items) {
      if (item.maxQuantity !== undefined && item.quantity > item.maxQuantity) {
        return `Товар "${item.name}": доступно только ${item.maxQuantity} шт., а в корзине ${item.quantity}`;
      }
    }
    return null;
  }, [items]);

  const addressError = useMemo(() => {
    if (!deliveryAddress.recipient_name.trim()) {
      return "Введите имя получателя";
    }
    if (!deliveryAddress.recipient_phone.trim()) {
      return "Введите телефон получателя";
    }
    if (!deliveryAddress.delivery_address.trim()) {
      return "Введите адрес доставки";
    }
    if (!deliveryAddress.delivery_city.trim()) {
      return "Введите город доставки";
    }
    return null;
  }, [deliveryAddress]);

  const payloadItems = useMemo(
    () =>
      items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price,
      })),
    [items],
  );

  if (!items.length) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 text-center">
        <h1 className="text-2xl font-semibold">Корзина пуста</h1>
        <p className="mt-2 text-slate-600">Добавьте товары, чтобы продолжить оплату.</p>
      </section>
    );
  }

  const handleAddressChange = (field: keyof DeliveryAddress, value: string) => {
    setDeliveryAddress((prev) => ({ ...prev, [field]: value }));
  };

  const handleCheckout = async () => {
    try {
      setIsSubmitting(true);
      setError(null);

      if (availabilityError) {
        throw new Error(availabilityError);
      }

      if (addressError) {
        throw new Error(addressError);
      }

      const order = await updateCart({
        order_products: payloadItems,
        delivery_address: deliveryAddress,
      });
      const invoice = await createInvoice({
        order_id: order.id,
        amount: order.amount,
        method: "stripe",
      });

      if (!invoice.link) {
        throw new ApiError("Ссылка на оплату не получена", 400);
      }

      window.location.href = invoice.link;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : (err as Error).message || "Не удалось создать оплату");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="my-10 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-semibold">Оформление заказа</h1>
        <button
          type="button"
          onClick={() => navigate("/cart")}
          className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-600"
        >
          Вернуться в корзину
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold">Ваш заказ</h2>
        <ul className="mt-4 space-y-2 text-sm text-slate-600">
          {items.map((item) => (
            <li key={item.product_id} className="flex items-center justify-between">
              <span>
                {item.name} × {item.quantity}
              </span>
              <span>{formatPrice(item.price * item.quantity)}</span>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-4">
          <span className="text-sm text-slate-500">Итого</span>
          <span className="text-xl font-semibold">{formatPrice(totalAmount)}</span>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold mb-4">Адрес доставки</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Имя получателя *
            </label>
            <input
              type="text"
              value={deliveryAddress.recipient_name}
              onChange={(e) => handleAddressChange("recipient_name", e.target.value)}
              placeholder="Иван Иванов"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Телефон *
            </label>
            <input
              type="tel"
              value={deliveryAddress.recipient_phone}
              onChange={(e) => handleAddressChange("recipient_phone", e.target.value)}
              placeholder="+7 (999) 123-45-67"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="md:col-span-2 space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Город *
            </label>
            <input
              type="text"
              value={deliveryAddress.delivery_city}
              onChange={(e) => handleAddressChange("delivery_city", e.target.value)}
              placeholder="Москва"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="md:col-span-2 space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Адрес доставки *
            </label>
            <input
              type="text"
              value={deliveryAddress.delivery_address}
              onChange={(e) => handleAddressChange("delivery_address", e.target.value)}
              placeholder="ул. Примерная, д. 10, кв. 50"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Индекс
            </label>
            <input
              type="text"
              value={deliveryAddress.delivery_zip || ""}
              onChange={(e) => handleAddressChange("delivery_zip", e.target.value)}
              placeholder="123456"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="md:col-span-2 space-y-2">
            <label className="text-sm font-medium text-slate-700">
              Комментарий к заказу
            </label>
            <textarea
              value={deliveryAddress.delivery_notes || ""}
              onChange={(e) => handleAddressChange("delivery_notes", e.target.value)}
              placeholder="Домофон, код, ориентир и т.д."
              rows={2}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold">Оплата</h2>
        <p className="mt-2 text-sm text-slate-600">
          Мы используем Stripe (тестовый режим). Для оплаты используйте тестовую
          карту 4242 4242 4242 4242.
        </p>

        {availabilityError ? (
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <p className="font-semibold">Внимание!</p>
            {availabilityError}
            <button
              type="button"
              onClick={() => navigate("/cart")}
              className="mt-2 text-sm font-semibold text-amber-700 underline"
            >
              Вернуться в корзину для исправления
            </button>
          </div>
        ) : null}

        {addressError ? (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {addressError}
          </div>
        ) : null}

        {error ? (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <button
          type="button"
          onClick={handleCheckout}
          disabled={isSubmitting || !!availabilityError || !!addressError}
          className="mt-4 rounded border border-amber-500 px-6 py-3 font-semibold text-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Создаем оплату..." : "Перейти к оплате"}
        </button>
      </div>
    </section>
  );
}
