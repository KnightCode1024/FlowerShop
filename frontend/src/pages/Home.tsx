import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import mainFlower from "../assets/images/main_flower.png";
import { ApiError } from "../api/authApi";
import { getProducts, type ProductListItem } from "../api/catalogApi";
import ProductCard from "../components/ProductCard";
import About from "../components/buttons/About.tsx";

import "../styles/App.css";

export default function Home() {
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    const loadProducts = async () => {
      try {
        const data = await getProducts({ offset: 0, limit: 8, in_stock: true });
        if (isActive) {
          setProducts(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось загрузить товары");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadProducts();

    return () => {
      isActive = false;
    };
  }, []);

  const highlights = [
    {
      title: "Свежие поставки каждый день",
      description: "Работаем с проверенными фермами и отбираем лучшие стебли.",
    },
    {
      title: "Быстрая доставка",
      description: "Привезем букет в день заказа или к точному времени.",
    },
    {
      title: "Авторские подборки",
      description: "Соберем композицию под ваш стиль, повод и бюджет.",
    },
  ];

  return (
    <section className="w-full">
      <div className="flex flex-col gap-10">
        <div className="grid grid-cols-1 gap-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-[1.1fr_0.9fr]">
          <div className="flex flex-col justify-center gap-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              Магазин цветов
            </p>
            <h1 className="text-4xl font-bold text-slate-900 sm:text-5xl">
              Свежие букеты и композиции для любого повода
            </h1>
            <p className="text-base text-slate-600">
              Быстрая доставка, авторские подборки и гарантия свежести. Выберите букет в каталоге
              или расскажите нам о вашем событии.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/catalog"
                className="rounded bg-yellow-500 px-5 py-3 font-semibold text-black"
              >
                Перейти в каталог
              </Link>
              <About />
            </div>
          </div>
          <div className="overflow-hidden rounded-2xl border border-slate-100">
            <img src={mainFlower} alt="Свежие букеты" className="h-full w-full object-cover" />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {highlights.map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <h3 className="text-lg font-semibold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-900 px-6 py-8 text-white">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Хит недели</h2>
              <p className="text-sm text-slate-200">
                Сезонные букеты со скидкой и открыткой в подарок.
              </p>
            </div>
            <Link
              to="/catalog"
              className="w-fit rounded bg-white px-4 py-2 font-semibold text-slate-900"
            >
              Смотреть предложения
            </Link>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">Популярные товары</h2>
            <p className="text-sm text-slate-500">
              Подборка свежих букетов, которые заказывают чаще всего.
            </p>
          </div>
          <Link to="/catalog" className="text-sm font-semibold text-yellow-500">
            Весь каталог →
          </Link>
        </div>

        {error ? (
          <p className="my-3 rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
        ) : null}

        {isLoading ? (
          <p className="py-6 text-center text-slate-500">Загрузка...</p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
