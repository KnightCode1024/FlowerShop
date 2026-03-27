import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAdminUsers } from "../../api/adminApi";
import type { UserResponse } from "../../api/authApi";
import { useAuth } from "../../auth/useAuth";
import { formatRole } from "../../utils/formatRole";

export default function AdminUsers() {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase?.() ?? "";
  const [items, setItems] = useState<UserResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAdminUsers(0, 100);
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
        Недостаточно прав для управления пользователями.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Пользователи</h1>
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
                <th className="px-4 py-3 font-medium">Эл. почта</th>
                <th className="px-4 py-3 font-medium">Имя</th>
                <th className="px-4 py-3 font-medium">Роль</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-600">{user.id}</td>
                  <td className="px-4 py-3 text-slate-600">{user.email}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {user.username}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatRole(user.role)}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/admin/users/${user.id}`}
                      className="text-slate-700 hover:text-slate-900"
                    >
                      Редактировать
                    </Link>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-slate-500" colSpan={5}>
                    Нет пользователей.
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
