import { FormEvent, useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../api/authApi";
import { useAuth } from "../auth/useAuth";

export default function Otp() {
  const navigate = useNavigate();
  const location = useLocation();
  const { submitOtp, resendOtp, isOtpPending, otpEmail } = useAuth();

  const [otpCode, setOtpCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  const fromPath =
    (location.state as { fromPath?: string | undefined })?.fromPath ?? "/profile";

  useEffect(() => {
    if (cooldown <= 0) {
      return;
    }
    const timer = window.setTimeout(() => {
      setCooldown((prev) => prev - 1);
    }, 1000);
    return () => window.clearTimeout(timer);
  }, [cooldown]);

  if (!isOtpPending) {
    return <Navigate to="/login" replace />;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await submitOtp(otpCode);
      navigate(fromPath, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Проверка OTP не удалась");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onResend() {
    if (cooldown > 0) {
      return;
    }

    setResendMessage(null);
    setError(null);
    setIsResending(true);

    try {
      await resendOtp();
      setResendMessage("Новый код OTP отправлен.");
      setCooldown(30);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отправить код OTP повторно");
    } finally {
      setIsResending(false);
    }
  }

  return (
    <section className="mx-auto mt-10 w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="mb-2 text-2xl font-bold">Проверка OTP</h1>
      <p className="mb-6 text-sm text-slate-600">
        Введите код OTP, отправленный на {otpEmail ?? "вашу почту"}.
      </p>

      {error ? (
        <p className="mb-4 rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
      ) : null}

      {resendMessage ? (
        <p className="mb-4 rounded bg-green-100 p-3 text-sm text-green-800">
          {resendMessage}
        </p>
      ) : null}

      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-sm text-slate-600">Код</span>
          <input
            type="text"
            required
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value)}
            className="rounded border border-slate-300 bg-white px-3 py-2 outline-none focus:border-slate-500"
            placeholder="123456"
          />
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded bg-yellow-500 px-4 py-2 font-semibold text-black disabled:opacity-60"
        >
          {isSubmitting ? "Проверяем..." : "Подтвердить"}
        </button>
      </form>

      <button
        type="button"
        onClick={onResend}
        disabled={isResending || cooldown > 0}
      className="mt-4 rounded border border-yellow-500 px-4 py-2 text-sm font-semibold text-yellow-400 disabled:opacity-60"
    >
      {isResending
        ? "Отправляем..."
        : cooldown > 0
          ? `Повторить через ${cooldown} сек.`
          : "Отправить код снова"}
    </button>
  </section>
);
}
