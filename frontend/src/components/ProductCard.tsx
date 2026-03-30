import { useState } from "react";
import { Link } from "react-router-dom";
import { formatPrice, type ProductListItem } from "../api/catalogApi";
import { useCart } from "../cart/useCart";
import QuantitySelector from "./QuantitySelector";

interface ProductCardProps {
  product: ProductListItem;
}

export default function ProductCard({ product }: ProductCardProps) {
  const { addItem, getItemQuantity } = useCart();
  const [quantity, setQuantity] = useState(1);
  const cartQuantity = getItemQuantity(product.id);
  const maxAvailable = product.quantity;
  const canAddToCart = product.in_stock && cartQuantity < maxAvailable;

  const handleAddToCart = () => {
    if (canAddToCart) {
      addItem({
        product_id: product.id,
        name: product.name,
        price: Number(product.price),
        image_url: product.main_image_url,
      }, quantity, maxAvailable);
      setQuantity(1);
    }
  };

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
            {product.in_stock ? `${product.quantity} шт.` : "Нет в наличии"}
          </span>
        </div>

        <p className="line-clamp-2 min-h-11 text-sm text-slate-600">
          {product.description ?? "Описание товара отсутствует"}
        </p>

        <p className="text-sm text-slate-500">{product.category_name}</p>

        <div className="mt-auto flex flex-col gap-3 pt-2">
          <p className="text-xl font-bold">
            {formatPrice(product.price)}
          </p>

          {product.in_stock ? (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between gap-2">
                <QuantitySelector
                  value={quantity}
                  maxValue={Math.min(maxAvailable, maxAvailable - cartQuantity)}
                  onChange={setQuantity}
                />
                <button
                  type="button"
                  onClick={handleAddToCart}
                  disabled={!canAddToCart}
                  className="flex-1 whitespace-nowrap rounded border border-amber-500 px-4 py-2 text-sm font-semibold text-amber-700 transition hover:bg-amber-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {cartQuantity > 0 ? `В корзине: ${cartQuantity}` : "В корзину"}
                </button>
              </div>
              <Link
                to={`/products/${product.id}`}
                className="text-center text-sm font-semibold text-yellow-600 transition hover:text-yellow-700"
              >
                Подробнее
              </Link>
            </div>
          ) : (
            <button
              type="button"
              disabled
              className="w-full rounded border border-slate-300 bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-400 disabled:cursor-not-allowed"
            >
              Нет в наличии
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
