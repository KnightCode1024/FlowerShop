import { useEffect, useState } from "react";
import { getAdminInvoices, type InvoiceItem } from "../../api/adminApi";
import { formatPrice } from "../../api/catalogApi";

export default function AdminInvoices() {
  const [items, setItems] = useState<InvoiceItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAdminInvoices();
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Счета</h1>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-slate-600">Загрузка...</div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">UID</th>
                <th className="px-4 py-3 font-medium">Заказ</th>
                <th className="px-4 py-3 font-medium">Пользователь</th>
                <th className="px-4 py-3 font-medium">Сумма</th>
                <th className="px-4 py-3 font-medium">Статус</th>
                <th className="px-4 py-3 font-medium">Метод</th>
                <th className="px-4 py-3 font-medium">Ссылка</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((invoice) => (
                <tr key={invoice.uid} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{invoice.uid}</td>
                  <td className="px-4 py-3 text-slate-600">{invoice.order_id}</td>
                  <td className="px-4 py-3 text-slate-600">{invoice.user_id}</td>
                  <td className="px-4 py-3 text-slate-900">
                    {formatPrice(invoice.amount)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{invoice.status}</td>
                  <td className="px-4 py-3 text-slate-600">{invoice.method}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {invoice.link ? (
                      <a
                        href={invoice.link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-slate-700 hover:text-slate-900"
                      >
                        открыть
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-slate-500" colSpan={7}>
                    Нет счетов.
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
