import { Link } from "react-router-dom";
import { formatPrice, type ProductListItem } from "../api/catalogApi";
import { useCart } from "../cart/useCart";

interface ProductCardProps {
  product: ProductListItem;
}

export default function ProductCard({ product }: ProductCardProps) {
  const { addItem } = useCart();

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      {product.main_image_url ? (
        <img
          src={product.main_image_url}
          alt={product.name}
          className="h-52 w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-52 items-center justify-center bg-slate-50 text-sm text-slate-500">
          Нет изображения
        </div>
      )}

      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="line-clamp-2 text-lg font-semibold">{product.name}</h3>
          <span className="shrink-0 rounded bg-yellow-500 px-2 py-1 text-xs font-semibold text-black">
            {product.in_stock ? "В наличии" : "Нет в наличии"}
          </span>
        </div>

        <p className="line-clamp-2 min-h-11 text-sm text-slate-600">
          {product.description ?? "Описание товара отсутствует"}
        </p>

        <p className="text-sm text-slate-500">{product.category_name}</p>

        <div className="mt-auto flex items-center justify-between pt-2">
          <p className="text-xl font-bold">
            {formatPrice(product.price)}
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() =>
                addItem({
                  product_id: product.id,
                  name: product.name,
                  price: Number(product.price),
                  image_url: product.main_image_url,
                })
              }
              disabled={!product.in_stock}
              className="rounded border border-amber-500 px-3 py-1 text-sm font-semibold text-amber-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              В корзину
            </button>
            <Link
              to={`/products/${product.id}`}
              className="rounded border border-yellow-500 px-3 py-1 text-sm font-semibold text-yellow-500 transition hover:bg-amber-500 hover:text-white"
            >
              Подробнее
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}
