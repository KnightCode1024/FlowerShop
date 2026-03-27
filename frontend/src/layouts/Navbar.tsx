import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "text-slate-900" : "text-slate-600";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const role = user?.role?.toLowerCase?.() ?? "";
  const canOpenAdmin = role === "admin" || role === "employee";

  function closeMenu() {
    setIsOpen(false);
  }

  return (
    <header className="relative border-b border-slate-200 bg-white p-4">
      <div className="flex items-center gap-4">
        <NavLink to="/" className="w-full text-2xl font-bold" onClick={closeMenu}>
          Наши Цветы®
        </NavLink>

        <button
          type="button"
          aria-label="Переключить меню"
          className="rounded border border-slate-300 px-3 py-2 text-sm font-semibold md:hidden"
          onClick={() => setIsOpen((prev) => !prev)}
        >
          {isOpen ? "Закрыть" : "Меню"}
        </button>

        <nav className="ml-auto hidden flex-row gap-5 text-sm font-semibold md:flex md:text-base">
          <NavLink to="/" className={navLinkClass}>
            Главная
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            О нас
          </NavLink>
          <NavLink to="/catalog" className={navLinkClass}>
            Каталог
          </NavLink>

          {isAuthenticated ? (
            <>
              {canOpenAdmin ? (
                <NavLink to="/admin/products" className={navLinkClass}>
                  Админка
                </NavLink>
              ) : null}
              <NavLink to="/profile" className={navLinkClass}>
                Профиль
              </NavLink>
              <button
                type="button"
                onClick={logout}
                className="cursor-pointer text-slate-600"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={navLinkClass}>
                Войти
              </NavLink>
              <NavLink to="/register" className={navLinkClass}>
                Регистрация
              </NavLink>
            </>
          )}
        </nav>
      </div>

      {isOpen ? (
        <nav className="mt-3 flex flex-col gap-3 border-t border-slate-200 pt-3 text-sm font-semibold md:hidden">
          <NavLink to="/" className={navLinkClass} onClick={closeMenu}>
            Главная
          </NavLink>
          <NavLink to="/about" className={navLinkClass} onClick={closeMenu}>
            О нас
          </NavLink>
          <NavLink to="/catalog" className={navLinkClass} onClick={closeMenu}>
            Каталог
          </NavLink>

          {isAuthenticated ? (
            <>
              {canOpenAdmin ? (
                <NavLink
                  to="/admin/products"
                  className={navLinkClass}
                  onClick={closeMenu}
                >
                  Админка
                </NavLink>
              ) : null}
              <NavLink to="/profile" className={navLinkClass} onClick={closeMenu}>
                Профиль
              </NavLink>
              <button
                type="button"
                onClick={() => {
                  closeMenu();
                  logout();
                }}
                className="w-fit cursor-pointer text-red-500"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={navLinkClass} onClick={closeMenu}>
                Войти
              </NavLink>
              <NavLink to="/register" className={navLinkClass} onClick={closeMenu}>
                Регистрация
              </NavLink>
            </>
          )}
        </nav>
      ) : null}
    </header>
  );
}
