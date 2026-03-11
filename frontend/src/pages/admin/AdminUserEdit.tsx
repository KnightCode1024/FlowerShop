import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  getAdminUser,
  updateAdminUser,
  type AdminUserUpdatePayload,
} from "../../api/adminApi";
import type { UserResponse } from "../../api/authApi";
import { useAuth } from "../../auth/useAuth";

const EMPTY_FORM: AdminUserUpdatePayload = {
  email: "",
  username: "",
  password: "",
};

export default function AdminUserEdit() {
  const { user: currentUser } = useAuth();
  const role = currentUser?.role?.toLowerCase?.() ?? "";
  const { userId } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState<AdminUserUpdatePayload>(EMPTY_FORM);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const userIdNumber = useMemo(() => {
    if (!userId) {
      return null;
    }
    const parsed = Number(userId);
    return Number.isFinite(parsed) ? parsed : null;
  }, [userId]);

  useEffect(() => {
    if (role !== "admin") {
      return;
    }
    let isMounted = true;
    const load = async () => {
      if (!userIdNumber) {
        setError("Некорректный идентификатор пользователя");
        setIsLoading(false);
        return;
      }
      setIsLoading(true);
      setError(null);
      try {
        const data = await getAdminUser(userIdNumber);
        if (!isMounted) {
          return;
        }
        setUser(data);
        setForm({
          email: data.email,
          username: data.username,
          password: "",
        });
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
  }, [role, userIdNumber]);

  if (role !== "admin") {
    return (
      <div className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
        Недостаточно прав для управления пользователями.
      </div>
    );
  }

  const handleChange = (
    field: keyof AdminUserUpdatePayload,
    value: string,
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!userIdNumber) {
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const payload: AdminUserUpdatePayload = {};
      if (form.email) {
        payload.email = form.email;
      }
      if (form.username) {
        payload.username = form.username;
      }
      if (form.password) {
        payload.password = form.password;
      }
      await updateAdminUser(userIdNumber, payload);
      navigate("/admin/users");
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
          <Link to="/admin/users" className="text-sm text-slate-500">
            ← Назад к списку
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">
            Редактирование пользователя
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
                Email
              </label>
              <input
                type="email"
                value={form.email ?? ""}
                onChange={(e) => handleChange("email", e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">
                Имя пользователя
              </label>
              <input
                type="text"
                value={form.username ?? ""}
                onChange={(e) => handleChange("username", e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <label className="text-sm font-medium text-slate-700">
                Новый пароль
              </label>
              <input
                type="password"
                value={form.password ?? ""}
                onChange={(e) => handleChange("password", e.target.value)}
                placeholder="Оставьте пустым, если менять не нужно"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
            Роль пользователя: <span className="font-medium">{user?.role}</span>
          </div>

          <div className="flex items-center justify-end gap-3">
            <Link
              to="/admin/users"
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
