import { useEffect, useState, type FormEvent } from "react";
import {
  createAdminPromocode,
  deleteAdminPromocode,
  getAdminPromocodes,
  updateAdminPromocode,
  type PromocodeItem,
} from "../../api/adminApi";

export default function AdminPromocodes() {
  const [items, setItems] = useState<PromocodeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [code, setCode] = useState("");
  const [maxCount, setMaxCount] = useState("1");
  const [percent, setPercent] = useState("5");

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAdminPromocodes();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const resetForm = () => {
    setEditingId(null);
    setCode("");
    setMaxCount("1");
    setPercent("5");
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    const maxCountValue = Number(maxCount);
    const percentValue = Number(percent);
    if (!Number.isFinite(maxCountValue) || maxCountValue < 1) {
      setError("Укажите корректный лимит активаций");
      return;
    }
    if (!Number.isFinite(percentValue) || percentValue <= 0) {
      setError("Укажите корректный процент скидки");
      return;
    }
    setIsSaving(true);
    try {
      if (editingId) {
        await updateAdminPromocode(editingId, {
          id: editingId,
          code: code.trim() ? code.trim() : null,
          max_count_activators: maxCountValue,
          percent: percentValue,
        });
      } else {
        await createAdminPromocode({
          code: code.trim() ? code.trim() : null,
          max_count_activators: maxCountValue,
          percent: percentValue,
        });
      }
      resetForm();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка сохранения");
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (promo: PromocodeItem) => {
    setEditingId(promo.id);
    setCode(promo.code ?? "");
    setMaxCount(String(promo.max_count_activators));
    setPercent(String(promo.percent));
  };

  const handleDelete = async (promoId: number) => {
    if (!window.confirm("Удалить промокод?")) {
      return;
    }
    setError(null);
    try {
      await deleteAdminPromocode(promoId);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Промокоды</h1>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid gap-4 rounded-lg border border-slate-200 bg-white p-4 md:grid-cols-4"
      >
        <div className="md:col-span-1">
          <label className="text-sm font-medium text-slate-700">
            Код (опционально)
          </label>
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="AUTO"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">
            Максимум активаций
          </label>
          <input
            type="number"
            min="1"
            value={maxCount}
            onChange={(e) => setMaxCount(e.target.value)}
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">
            Процент скидки
          </label>
          <input
            type="number"
            min="1"
            step="0.5"
            value={percent}
            onChange={(e) => setPercent(e.target.value)}
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex items-end gap-3">
          <button
            type="submit"
            disabled={isSaving}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800 disabled:opacity-60"
          >
            {isSaving ? "Сохранение..." : editingId ? "Обновить" : "Создать"}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={resetForm}
              className="rounded-md border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              Отмена
            </button>
          )}
        </div>
      </form>

      {isLoading ? (
        <div className="text-slate-600">Загрузка...</div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Код</th>
                <th className="px-4 py-3 font-medium">Использований</th>
                <th className="px-4 py-3 font-medium">Лимит</th>
                <th className="px-4 py-3 font-medium">Скидка</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{item.id}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {item.code ?? "AUTO"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {item.count_activation}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {item.max_count_activators}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {Number(item.percent)}%
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-3">
                      <button
                        type="button"
                        onClick={() => handleEdit(item)}
                        className="text-slate-700 hover:text-slate-900"
                      >
                        Редактировать
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(item.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Удалить
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-slate-500" colSpan={6}>
                    Нет промокодов.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
