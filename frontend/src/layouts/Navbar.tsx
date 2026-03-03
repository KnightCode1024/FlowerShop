import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "text-yellow-400" : "text-gray-200";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="flex w-full items-center gap-6 border-b border-gray-800 p-4">
      <NavLink to="/" className="w-full text-2xl font-bold">
        Our Blooms R
      </NavLink>

      <nav className="ml-auto flex flex-row gap-5 text-sm font-semibold sm:text-base">
        <NavLink to="/" className={navLinkClass}>
          HOME
        </NavLink>
        <NavLink to="/about" className={navLinkClass}>
          ABOUT
        </NavLink>

        {isAuthenticated ? (
          <>
            <NavLink to="/profile" className={navLinkClass}>
              PROFILE
            </NavLink>
            <button
              type="button"
              onClick={logout}
              className="cursor-pointer text-red-300"
            >
              LOGOUT
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={navLinkClass}>
              LOGIN
            </NavLink>
            <NavLink to="/register" className={navLinkClass}>
              REGISTER
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
