import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

const ALLOWED_ROLES = new Set(["admin", "employee"]);

export default function AdminRoute() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="py-10 text-center">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const role = user?.role?.toLowerCase?.() ?? "";
  if (!user || !ALLOWED_ROLES.has(role)) {
    return (
      <div className="py-10 text-center text-red-600">
        Недостаточно прав для доступа к админке.
      </div>
    );
  }

  return <Outlet />;
}
