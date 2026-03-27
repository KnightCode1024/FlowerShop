import { Link } from "react-router-dom";
import { formatPrice } from "../api/catalogApi";
import { useCart } from "../cart/useCart";

export default function Cart() {
  const { items, totalAmount, removeItem, updateQuantity, clear } = useCart();

  if (!items.length) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 text-center">
        <h1 className="text-2xl font-semibold">Корзина пуста</h1>
        <p className="mt-2 text-slate-600">
          Добавьте товары из каталога и возвращайтесь к оформлению.
        </p>
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
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-semibold">Корзина</h1>
        <button
          type="button"
          onClick={clear}
          className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-600"
        >
          Очистить
        </button>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <article
            key={item.product_id}
            className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-center"
          >
            <div className="flex items-center gap-4">
              <div className="h-20 w-20 overflow-hidden rounded-lg bg-slate-100">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="h-full w-full object-cover"
                  />
                ) : null}
              </div>
              <div>
                <h2 className="text-lg font-semibold">{item.name}</h2>
                <p className="text-slate-600">{formatPrice(item.price)}</p>
              </div>
            </div>

            <div className="flex flex-1 items-center justify-between gap-4">
              <label className="flex items-center gap-2 text-sm text-slate-600">
                Кол-во
                <input
                  type="number"
                  min={1}
                  value={item.quantity}
                  onChange={(event) =>
                    updateQuantity(
                      item.product_id,
                      Number.isFinite(Number(event.target.value))
                        ? Number(event.target.value)
                        : 1,
                    )
                  }
                  className="w-20 rounded border border-slate-300 px-2 py-1"
                />
              </label>
              <p className="text-lg font-semibold">
                {formatPrice(item.price * item.quantity)}
              </p>
              <button
                type="button"
                onClick={() => removeItem(item.product_id)}
                className="rounded border border-red-200 px-3 py-1 text-sm text-red-600"
              >
                Удалить
              </button>
            </div>
          </article>
        ))}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4">
        <div>
          <p className="text-sm text-slate-500">Итого</p>
          <p className="text-2xl font-semibold">{formatPrice(totalAmount)}</p>
        </div>
        <Link
          to="/checkout"
          className="rounded border border-amber-500 px-6 py-3 font-semibold text-amber-700"
        >
          Перейти к оплате
        </Link>
      </div>
    </section>
  );
}
