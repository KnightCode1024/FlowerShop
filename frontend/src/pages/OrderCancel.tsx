import { Link } from "react-router-dom";

export default function OrderCancel() {
  return (
    <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 text-center">
      <h1 className="text-2xl font-semibold">Оплата отменена</h1>
      <p className="mt-3 text-slate-600">
        Вы можете попробовать оплатить снова или вернуться в корзину.
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-3">
        <Link
          to="/cart"
          className="rounded border border-amber-500 px-4 py-2 font-semibold text-amber-700"
        >
          Вернуться в корзину
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
