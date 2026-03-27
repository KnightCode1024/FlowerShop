export function formatRole(role?: string | null): string {
  if (!role) {
    return "—";
  }

  switch (role.toLowerCase()) {
    case "admin":
      return "Администратор";
    case "employee":
      return "Сотрудник";
    case "user":
      return "Пользователь";
    default:
      return role;
  }
}
