import { useAuth } from "../auth/useAuth";

export default function Profile() {
  const { user, refreshProfile } = useAuth();

  if (!user) {
    return <div className="py-10 text-center">User not found</div>;
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="mb-6 text-2xl font-bold">Profile</h1>

      <div className="space-y-3 text-sm sm:text-base">
        <p>
          <span className="text-slate-500">ID:</span> {user.id}
        </p>
        <p>
          <span className="text-slate-500">Email:</span> {user.email}
        </p>
        <p>
          <span className="text-slate-500">Username:</span> {user.username}
        </p>
        <p>
          <span className="text-slate-500">Role:</span> {user.role}
        </p>
      </div>

      <button
        type="button"
        onClick={refreshProfile}
        className="mt-6 rounded border border-yellow-400 px-4 py-2 font-semibold text-yellow-400"
      >
        Refresh profile
      </button>
    </section>
  );
}
