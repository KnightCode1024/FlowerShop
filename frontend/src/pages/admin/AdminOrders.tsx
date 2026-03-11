import { useEffect, useState } from "react";
import { deleteAdminOrder, getAdminOrders, type OrderItem } from "../../api/adminApi";
import { formatPrice } from "../../api/catalogApi";
import { useAuth } from "../../auth/useAuth";

function summarizeItems(items: OrderItem["order_products"]): string {
  if (!items || items.length === 0) {
    return "Нет позиций";
  }
  const totalQty = items.reduce((sum, item) => sum + item.quantity, 0);
  return `${items.length} поз. / ${totalQty} шт.`;
}

export default function AdminOrders() {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase?.() ?? "";
  const [items, setItems] = useState<OrderItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAdminOrders();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (role !== "admin") {
      return;
    }
    void load();
  }, [role]);

  if (role !== "admin") {
    return (
      <div className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
        Недостаточно прав для просмотра заказов.
      </div>
    );
  }

  const handleDelete = async (orderId: number) => {
    if (!window.confirm("Удалить заказ?")) {
      return;
    }
    setError(null);
    try {
      await deleteAdminOrder(orderId);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Заказы</h1>
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
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Пользователь</th>
                <th className="px-4 py-3 font-medium">Статус</th>
                <th className="px-4 py-3 font-medium">Сумма</th>
                <th className="px-4 py-3 font-medium">Позиции</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{order.id}</td>
                  <td className="px-4 py-3 text-slate-600">{order.user_id}</td>
                  <td className="px-4 py-3 text-slate-600">{order.status}</td>
                  <td className="px-4 py-3 text-slate-900">
                    {formatPrice(order.amount)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    <details className="cursor-pointer">
                      <summary>{summarizeItems(order.order_products)}</summary>
                      <div className="mt-2 space-y-1 text-xs text-slate-600">
                        {order.order_products?.map((item, index) => (
                          <div key={`${item.product_id}-${index}`}>
                            Товар #{item.product_id} · {item.quantity} шт. ·{" "}
                            {formatPrice(item.price)}
                          </div>
                        ))}
                      </div>
                    </details>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => handleDelete(order.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-slate-500" colSpan={6}>
                    Нет заказов.
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
