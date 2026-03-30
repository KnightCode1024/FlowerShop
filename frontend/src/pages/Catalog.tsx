import { FormEvent, useEffect, useMemo, useState } from "react";
import { ApiError } from "../api/authApi";
import {
  getCategories,
  getProducts,
  type CategoryListItem,
  type ProductFilters,
  type ProductListItem,
} from "../api/catalogApi";
import ProductCard from "../components/ProductCard";

const PAGE_SIZE = 24;

export default function Catalog() {
  const [categories, setCategories] = useState<CategoryListItem[]>([]);
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [draftMinPrice, setDraftMinPrice] = useState("");
  const [draftMaxPrice, setDraftMaxPrice] = useState("");
  const [draftCategoryId, setDraftCategoryId] = useState("all");

  const [filters, setFilters] = useState<ProductFilters>({
    offset: 0,
    limit: PAGE_SIZE,
    in_stock: true,
  });

  useEffect(() => {
    let isActive = true;
    (async () => {
      try {
        const data = await getCategories(100, true);
        if (isActive) {
          setCategories(data);
        }
      } catch {
        if (isActive) {
          setCategories([]);
        }
      }
    })();
    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    setError(null);

    (async () => {
      try {
        const data = await getProducts(filters);
        if (isActive) {
          setProducts(data);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof ApiError ? err.message : "Не удалось загрузить каталог");
          setProducts([]);
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
  }, [filters]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const nextFilters: ProductFilters = {
      offset: 0,
      limit: PAGE_SIZE,
      in_stock: true,
    };

    if (draftMinPrice.trim()) {
      nextFilters.min_price = Number(draftMinPrice);
    }
    if (draftMaxPrice.trim()) {
      nextFilters.max_price = Number(draftMaxPrice);
    }
    if (draftCategoryId !== "all") {
      nextFilters.category_id = Number(draftCategoryId);
    }

    setFilters(nextFilters);
  }

  function resetFilters() {
    setDraftMinPrice("");
    setDraftMaxPrice("");
    setDraftCategoryId("all");
    setFilters({ offset: 0, limit: PAGE_SIZE, in_stock: true });
  }

  const subtitle = useMemo(() => {
    if (isLoading) {
      return "Загружаем товары...";
    }
    return `Показано товаров: ${products.length}`;
  }, [isLoading, products.length]);

  const currentPage = useMemo(() => {
    const offset = filters.offset ?? 0;
    const limit = filters.limit ?? PAGE_SIZE;
    return Math.floor(offset / limit) + 1;
  }, [filters.offset, filters.limit]);

  const canGoPrev = (filters.offset ?? 0) > 0;
  const canGoNext = products.length === (filters.limit ?? PAGE_SIZE);

  function goToPrevPage() {
    if (!canGoPrev || isLoading) {
      return;
    }

    setFilters((prev) => {
      const limit = prev.limit ?? PAGE_SIZE;
      const nextOffset = Math.max(0, (prev.offset ?? 0) - limit);
      return { ...prev, offset: nextOffset };
    });
  }

  function goToNextPage() {
    if (!canGoNext || isLoading) {
      return;
    }

    setFilters((prev) => {
      const limit = prev.limit ?? PAGE_SIZE;
      return { ...prev, offset: (prev.offset ?? 0) + limit };
    });
  }

  return (
    <section className="my-8 flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold">Каталог товаров</h1>
        <p className="text-sm text-slate-500">{subtitle}</p>
      </header>

      <form
        onSubmit={applyFilters}
        className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-5"
      >
        <input
          type="number"
          min={0}
          step="1"
          value={draftMinPrice}
          onChange={(e) => setDraftMinPrice(e.target.value)}
          placeholder="Цена от"
          className="rounded border border-slate-300 bg-white px-3 py-2 outline-none focus:border-slate-500"
        />
        <input
          type="number"
          min={0}
          step="1"
          value={draftMaxPrice}
          onChange={(e) => setDraftMaxPrice(e.target.value)}
          placeholder="Цена до"
          className="rounded border border-slate-300 bg-white px-3 py-2 outline-none focus:border-slate-500"
        />
        <select
          value={draftCategoryId}
          onChange={(e) => setDraftCategoryId(e.target.value)}
          className="rounded border border-slate-300 bg-white px-3 py-2 outline-none focus:border-slate-500"
        >
          <option value="all">Все категории</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="rounded bg-yellow-500 px-4 py-2 font-semibold text-black"
        >
          Применить
        </button>
        <button
          type="button"
          onClick={resetFilters}
          className="rounded border border-slate-300 bg-slate-50 px-4 py-2 font-semibold text-slate-700"
        >
          Сбросить
        </button>
      </form>

      {error ? (
        <p className="rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
      ) : null}

      {isLoading ? (
        <p className="py-8 text-center text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          <div className="mt-2 flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={goToPrevPage}
              disabled={!canGoPrev}
              className="rounded border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Назад
            </button>
            <span className="text-sm text-slate-600">Страница {currentPage}</span>
            <button
              type="button"
              onClick={goToNextPage}
              disabled={!canGoNext}
              className="rounded border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Вперед
            </button>
          </div>
        </>
      )}
    </section>
  );
}
