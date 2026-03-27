import { useAuth } from "../auth/useAuth";
import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../api/authApi";
import { getPurchases, type OrderItem } from "../api/orderApi";
import { formatRole } from "../utils/formatRole";

export default function Profile() {
  const { user, refreshProfile } = useAuth();
  const [purchases, setPurchases] = useState<OrderItem[] | null>(null);
  const [purchasesError, setPurchasesError] = useState<string | null>(null);
  const [loadingPurchases, setLoadingPurchases] = useState(false);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;

    setLoadingPurchases(true);
    setPurchasesError(null);

    getPurchases()
      .then((data) => {
        if (cancelled) return;
        setPurchases(data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError) setPurchasesError(err.message);
        else setPurchasesError("Не удалось загрузить покупки");
      })
      .finally(() => {
        if (cancelled) return;
        setLoadingPurchases(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user]);

  const purchasesSorted = useMemo(() => {
    if (!purchases) return [];
    return [...purchases].sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
  }, [purchases]);

  if (!user) {
    return <div className="py-10 text-center">Пользователь не найден</div>;
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-3xl space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-6 text-2xl font-bold">Профиль</h1>

        <div className="space-y-3 text-sm sm:text-base">
          <p>
            <span className="text-slate-500">ID:</span> {user.id}
          </p>
          <p>
            <span className="text-slate-500">Эл. почта:</span> {user.email}
          </p>
          <p>
            <span className="text-slate-500">Имя пользователя:</span>{" "}
            {user.username}
          </p>
          <p>
            <span className="text-slate-500">Роль:</span>{" "}
            {formatRole(user.role)}
          </p>
        </div>

        <button
          type="button"
          onClick={refreshProfile}
          className="mt-6 rounded border border-yellow-400 px-4 py-2 font-semibold text-yellow-400"
        >
          Обновить профиль
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-xl font-bold">Мои покупки</h2>
          <button
            type="button"
            onClick={() => {
              setLoadingPurchases(true);
              setPurchasesError(null);
              getPurchases()
                .then(setPurchases)
                .catch((err: unknown) => {
                  if (err instanceof ApiError) setPurchasesError(err.message);
                  else setPurchasesError("Не удалось загрузить покупки");
                })
                .finally(() => setLoadingPurchases(false));
            }}
            className="rounded border border-slate-300 px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Обновить
          </button>
        </div>

        {purchasesError ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {purchasesError}
          </div>
        ) : null}

        {loadingPurchases ? (
          <div className="text-sm text-slate-500">Загрузка…</div>
        ) : purchasesSorted.length === 0 ? (
          <div className="text-sm text-slate-500">Покупок пока нет</div>
        ) : (
          <div className="space-y-3">
            {purchasesSorted.map((order) => (
              <div
                key={order.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="font-semibold">Заказ #{order.id}</div>
                  <div className="text-sm text-slate-600">
                    {order.status} · {order.amount} ₽
                  </div>
                </div>

                <div className="mt-2 text-sm text-slate-600">
                  {order.order_products?.length ?? 0} поз.
                </div>

                {order.order_products?.length ? (
                  <ul className="mt-2 space-y-1 text-sm text-slate-700">
                    {order.order_products.slice(0, 5).map((item, idx) => (
                      <li key={`${order.id}-${item.product_id}-${idx}`}>
                        Товар #{item.product_id}: {item.quantity} × {item.price} ₽
                      </li>
                    ))}
                    {order.order_products.length > 5 ? (
                      <li className="text-slate-500">
                        …и ещё {order.order_products.length - 5}
                      </li>
                    ) : null}
                  </ul>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
