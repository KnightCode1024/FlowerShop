import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../api/authApi";
import { useAuth } from "../auth/useAuth";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginStart, isOtpPending, otpEmail } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fromPath = (location.state as { from?: { pathname?: string } })?.from
    ?.pathname;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await loginStart({ email, password });
      navigate("/otp", { replace: true, state: { fromPath } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-md rounded-xl border border-gray-700 p-6">
      <h1 className="mb-6 text-2xl font-bold">Sign in</h1>

      {isOtpPending && otpEmail ? (
        <p className="mb-4 rounded bg-yellow-100 p-3 text-sm text-black">
          OTP step is pending for {otpEmail}. Continue on the OTP page.
        </p>
      ) : null}

      {error ? (
        <p className="mb-4 rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
      ) : null}

      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-sm text-gray-300">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded border border-gray-600 bg-transparent px-3 py-2"
            placeholder="you@example.com"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm text-gray-300">Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border border-gray-600 bg-transparent px-3 py-2"
            placeholder="Password"
          />
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded bg-yellow-500 px-4 py-2 font-semibold text-black disabled:opacity-60"
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="mt-4 text-sm text-gray-400">
        No account?{" "}
        <Link to="/register" className="text-yellow-400 underline">
          Create one
        </Link>
      </p>
    </section>
  );
}
