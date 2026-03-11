import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const role = user?.role?.toLowerCase?.() ?? "";
  const isAdmin = role === "admin";
  const canManageCatalog = role === "admin" || role === "employee";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-lg font-semibold">
              FlowerShop
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              {canManageCatalog ? (
                <>
                  <Link
                    to="/admin/products"
                    className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
                  >
                    Товары
                  </Link>
                  <Link
                    to="/admin/categories"
                    className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
                  >
                    Категории
                  </Link>
                  <Link
                    to="/admin/promocodes"
                    className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
                  >
                    Промокоды
                  </Link>
                </>
              ) : null}
              <Link
                to="/admin/invoices"
                className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
              >
                Счета
              </Link>
              {isAdmin ? (
                <>
                  <Link
                    to="/admin/orders"
                    className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
                  >
                    Заказы
                  </Link>
                  <Link
                    to="/admin/users"
                    className="rounded-md px-3 py-1.5 text-slate-700 hover:bg-slate-100"
                  >
                    Пользователи
                  </Link>
                </>
              ) : null}
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            {user && (
              <span className="text-slate-600">
                {user.username} ({user.role})
              </span>
            )}
            <button
              type="button"
              onClick={logout}
              className="rounded-md border border-slate-200 px-3 py-1.5 text-slate-700 hover:bg-slate-100"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
