import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/authApi";
import { formatPrice } from "../api/catalogApi";
import { getOrders, type OrderItem } from "../api/orderApi";

export default function Orders() {
  const [orders, setOrders] = useState<OrderItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    (async () => {
      try {
        const data = await getOrders();
        if (isActive) {
          setOrders(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось загрузить заказы");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    })();
    return () => {
      isActive = false;
    };
  }, []);

  if (isLoading) {
    return <p className="py-10 text-center text-slate-500">Загрузка заказов...</p>;
  }

  if (error) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-red-300 bg-red-50 p-6 text-red-800">
        <p>{error}</p>
      </section>
    );
  }

  if (!orders.length) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 text-center">
        <h1 className="text-2xl font-semibold">Заказов пока нет</h1>
        <Link
          to="/catalog"
          className="mt-4 inline-block rounded border border-amber-500 px-4 py-2 font-semibold text-amber-700"
        >
          Перейти в каталог
        </Link>
      </section>
    );
  }

  return (
    <section className="my-10 space-y-6">
      <h1 className="text-3xl font-semibold">Мои заказы</h1>
      <div className="space-y-4">
        {orders.map((order) => (
          <article
            key={order.id}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm text-slate-500">Заказ #{order.id}</p>
                <p className="text-lg font-semibold">{formatPrice(order.amount)}</p>
              </div>
              <span className="rounded bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                {order.status}
              </span>
            </div>
            <div className="mt-3 text-sm text-slate-600">
              Товаров: {order.order_products?.length ?? 0}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
