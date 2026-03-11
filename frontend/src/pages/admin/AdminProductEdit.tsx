import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  createAdminProduct,
  getAdminCategories,
  getAdminProduct,
  updateAdminProduct,
  type ProductUpsertPayload,
} from "../../api/adminApi";
import type { CategoryListItem, ProductDetails } from "../../api/catalogApi";

const EMPTY_FORM: ProductUpsertPayload = {
  name: "",
  description: "",
  price: 0,
  in_stock: true,
  category_id: 0,
};

export default function AdminProductEdit() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const isNew = !productId || productId === "new";

  const [form, setForm] = useState<ProductUpsertPayload>(EMPTY_FORM);
  const [categories, setCategories] = useState<CategoryListItem[]>([]);
  const [existingImages, setExistingImages] = useState<ProductDetails["images"]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const productIdNumber = useMemo(() => {
    if (!productId) {
      return null;
    }
    const parsed = Number(productId);
    return Number.isFinite(parsed) ? parsed : null;
  }, [productId]);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [cats, product] = await Promise.all([
          getAdminCategories(),
          isNew || !productIdNumber ? Promise.resolve(null) : getAdminProduct(productIdNumber),
        ]);

        if (!isMounted) {
          return;
        }

        setCategories(cats);

        if (product) {
          setForm({
            name: product.name,
            description: product.description ?? "",
            price: Number(product.price),
            in_stock: product.in_stock,
            category_id: product.category_id,
          });
          setExistingImages(product.images ?? []);
        } else if (cats.length > 0) {
          setForm((prev) => ({
            ...prev,
            category_id: prev.category_id || cats[0].id,
          }));
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Ошибка загрузки");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void load();

    return () => {
      isMounted = false;
    };
  }, [isNew, productIdNumber]);

  const handleChange = (
    field: keyof ProductUpsertPayload,
    value: string | number | boolean,
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleFilesChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      setFiles([]);
      return;
    }
    setFiles(Array.from(event.target.files));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSaving(true);
    try {
      if (isNew) {
        await createAdminProduct(form, files);
      } else if (productIdNumber) {
        await updateAdminProduct(productIdNumber, form, files);
      }
      navigate("/admin/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка сохранения");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/admin/products" className="text-sm text-slate-500">
            ← Назад к списку
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">
            {isNew ? "Новый товар" : "Редактирование товара"}
          </h1>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-slate-600">Загрузка...</div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-lg border border-slate-200 bg-white p-6"
        >
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Название
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => handleChange("name", e.target.value)}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Категория
              </label>
              <select
                value={form.category_id}
                onChange={(e) => handleChange("category_id", Number(e.target.value))}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Цена
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={(e) => handleChange("price", Number(e.target.value))}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex items-center gap-3">
              <input
                id="in-stock"
                type="checkbox"
                checked={form.in_stock}
                onChange={(e) => handleChange("in_stock", e.target.checked)}
                className="h-4 w-4 rounded border-slate-300"
              />
              <label htmlFor="in-stock" className="text-sm text-slate-700">
                В наличии
              </label>
            </div>
            <div className="md:col-span-2 space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Описание
              </label>
              <textarea
                value={form.description ?? ""}
                onChange={(e) => handleChange("description", e.target.value)}
                rows={4}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-sm font-medium text-slate-700">
              Новые фотографии
            </div>
            <input
              type="file"
              multiple
              onChange={handleFilesChange}
              className="block text-sm text-slate-600"
            />
            {files.length > 0 && (
              <div className="text-sm text-slate-500">
                Выбрано файлов: {files.length}
              </div>
            )}
          </div>

          {!isNew && (
            <div className="space-y-3">
              <div className="text-sm font-medium text-slate-700">
                Текущая галерея
              </div>
              {existingImages.length === 0 ? (
                <div className="text-sm text-slate-500">Нет изображений.</div>
              ) : (
                <div className="flex flex-wrap gap-3">
                  {existingImages.map((img) => (
                    <div key={`${img.url}-${img.order}`} className="text-center">
                      <img
                        src={img.url}
                        alt={`Фото ${img.order}`}
                        className="h-24 w-24 rounded-md object-cover"
                      />
                      <div className="text-xs text-slate-500">
                        #{img.order} {img.is_primary ? "(main)" : ""}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="text-xs text-slate-500">
                Удаление изображений пока не реализовано через API.
              </div>
            </div>
          )}

          <div className="flex items-center justify-end gap-3">
            <Link
              to="/admin/products"
              className="rounded-md border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              Отмена
            </Link>
            <button
              type="submit"
              disabled={isSaving}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800 disabled:opacity-60"
            >
              {isSaving ? "Сохранение..." : "Сохранить"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
