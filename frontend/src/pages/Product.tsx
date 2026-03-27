import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/authApi";
import { formatPrice, getProduct, type ProductDetails } from "../api/catalogApi";
import { useCart } from "../cart/useCart";

export default function Product() {
  const { productId } = useParams();
  const { addItem } = useCart();
  const [product, setProduct] = useState<ProductDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = Number(productId);
    if (!Number.isFinite(id) || id <= 0) {
      setError("Некорректный ID товара");
      setIsLoading(false);
      return;
    }

    let isActive = true;
    (async () => {
      try {
        const data = await getProduct(id);
        if (isActive) {
          setProduct(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось загрузить товар");
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
  }, [productId]);

  const primaryImage = useMemo(() => {
    if (!product?.images?.length) {
      return null;
    }
    return product.images.find((image) => image.is_primary) ?? product.images[0];
  }, [product]);

  if (isLoading) {
    return <p className="py-10 text-center text-slate-500">Загрузка товара...</p>;
  }

  if (error || !product) {
    return (
      <section className="mx-auto mt-10 max-w-2xl rounded-xl border border-red-300 bg-red-50 p-6 text-red-800">
        <p>{error ?? "Товар не найден"}</p>
        <Link to="/catalog" className="mt-4 inline-block underline">
          Вернуться в каталог
        </Link>
      </section>
    );
  }

  return (
    <section className="my-10 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {primaryImage ? (
          <img
            src={primaryImage.url}
            alt={product.name}
            className="h-[420px] w-full object-cover"
          />
        ) : (
          <div className="flex h-[420px] items-center justify-center text-slate-500">
            Нет изображения
          </div>
        )}
      </div>

      <div className="flex flex-col gap-4">
        <p className="text-sm text-slate-500">{product.category.name}</p>
        <h1 className="text-4xl font-bold">{product.name}</h1>
        <p className="text-2xl font-semibold text-amber-700">
          {formatPrice(product.price)}
        </p>
        <p className="text-slate-700">
          {product.description ?? "Описание товара отсутствует."}
        </p>
        <p className="text-sm text-slate-600">
          Статус: {product.in_stock ? "в наличии" : "нет в наличии"}
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() =>
              addItem({
                product_id: product.id,
                name: product.name,
                price: Number(product.price),
                image_url: primaryImage?.url ?? null,
              })
            }
            disabled={!product.in_stock}
            className="rounded border border-amber-500 px-4 py-2 font-semibold text-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            В корзину
          </button>
          <Link
            to="/catalog"
            className="rounded border border-amber-500 px-4 py-2 font-semibold text-amber-700"
          >
            Назад в каталог
          </Link>
        </div>
      </div>
    </section>
  );
}
