import { useAuth } from "../auth/useAuth";

export default function Profile() {
  const { user, refreshProfile } = useAuth();

  if (!user) {
    return <div className="py-10 text-center">User not found</div>;
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-xl rounded-xl border border-gray-700 p-6">
      <h1 className="mb-6 text-2xl font-bold">Profile</h1>

      <div className="space-y-3 text-sm sm:text-base">
        <p>
          <span className="text-gray-400">ID:</span> {user.id}
        </p>
        <p>
          <span className="text-gray-400">Email:</span> {user.email}
        </p>
        <p>
          <span className="text-gray-400">Username:</span> {user.username}
        </p>
        <p>
          <span className="text-gray-400">Role:</span> {user.role}
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
