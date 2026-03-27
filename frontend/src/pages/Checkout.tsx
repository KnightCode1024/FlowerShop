import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { formatPrice } from "../api/catalogApi";
import { createInvoice, updateCart } from "../api/orderApi";
import { ApiError } from "../api/authApi";
import { useCart } from "../cart/useCart";

export default function Checkout() {
  const { items, totalAmount } = useCart();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleCheckout = async () => {
    try {
      setIsSubmitting(true);
      setError(null);

      const order = await updateCart(payloadItems);
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
      setError(err instanceof ApiError ? err.message : "Не удалось создать оплату");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="my-10 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-semibold">Оформление</h1>
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
        <h2 className="text-lg font-semibold">Оплата</h2>
        <p className="mt-2 text-sm text-slate-600">
          Мы используем Stripe (тестовый режим). Для оплаты используйте тестовую
          карту 4242 4242 4242 4242.
        </p>

        {error ? (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <button
          type="button"
          onClick={handleCheckout}
          disabled={isSubmitting}
          className="mt-4 rounded border border-amber-500 px-6 py-3 font-semibold text-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Создаем оплату..." : "Перейти к оплате"}
        </button>
      </div>
    </section>
  );
}
