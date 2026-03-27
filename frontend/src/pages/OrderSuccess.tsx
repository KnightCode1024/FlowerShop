import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/authApi";
import { processInvoice } from "../api/orderApi";
import { useCart } from "../cart/useCart";

export default function OrderSuccess() {
  const [params] = useSearchParams();
  const { clear } = useCart();
  const [message, setMessage] = useState<string>("Проверяем оплату...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const invoiceUid = params.get("invoice_uid");
    if (!invoiceUid) {
      setError("Не найден идентификатор счета");
      return;
    }

    let isActive = true;
    (async () => {
      try {
        const invoice = await processInvoice("stripe", invoiceUid);
        if (!isActive) {
          return;
        }
        if (invoice.status === "payed") {
          clear();
          setMessage("Оплата прошла успешно. Мы готовим ваш заказ.");
        } else {
          setMessage("Платеж в обработке. Статус заказа обновится позже.");
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось проверить оплату");
        }
      }
    })();

    return () => {
      isActive = false;
    };
  }, [clear, params]);

  if (error) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-red-300 bg-red-50 p-6 text-red-800">
        <p>{error}</p>
      </section>
    );
  }

  return (
    <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 text-center">
      <h1 className="text-2xl font-semibold">Спасибо за заказ</h1>
      <p className="mt-3 text-slate-600">{message}</p>
      <div className="mt-4 flex flex-wrap justify-center gap-3">
        <Link
          to="/orders"
          className="rounded border border-amber-500 px-4 py-2 font-semibold text-amber-700"
        >
          Мои заказы
        </Link>
        <Link
          to="/catalog"
          className="rounded border border-slate-300 px-4 py-2 text-slate-600"
        >
          В каталог
        </Link>
      </div>
    </section>
  );
}
