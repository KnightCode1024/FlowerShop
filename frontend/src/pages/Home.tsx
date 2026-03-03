import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import mainFlower from "../assets/images/main_flower.png";
import { ApiError } from "../api/authApi";
import { getProducts, type ProductListItem } from "../api/catalogApi";
import ProductCard from "../components/ProductCard";

export default function Home() {
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    (async () => {
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
    })();

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <div className="my-8 flex flex-col gap-10">
      <section className="grid grid-cols-1 items-center gap-6 lg:grid-cols-2">
        <div className="flex flex-col gap-5">
          <h1 className="text-5xl font-bold sm:text-6xl">Our Blooms R</h1>
          <p className="max-w-xl text-slate-600">
            Доставляем свежие цветы и авторские композиции по городу. Выбирайте
            букет для любого случая в нашем каталоге.
          </p>
          <div className="flex gap-3">
            <Link
              to="/catalog"
              className="rounded bg-yellow-500 px-5 py-3 font-semibold text-black"
            >
              Перейти в каталог
            </Link>
            <Link
              to="/about"
              className="rounded border border-slate-300 bg-white px-5 py-3 text-slate-700"
            >
              О магазине
            </Link>
          </div>
        </div>
        <img
          src={mainFlower}
          alt="Flowers"
          className="h-[420px] w-full rounded-2xl object-cover"
        />
      </section>

      <section className="flex flex-col gap-5">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-3xl font-bold">Популярные товары</h2>
          <Link to="/catalog" className="text-sm font-semibold text-yellow-400">
            Смотреть все
          </Link>
        </div>

        {error ? (
          <p className="rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
        ) : null}

        {isLoading ? (
          <p className="py-6 text-center text-slate-500">Загрузка...</p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
