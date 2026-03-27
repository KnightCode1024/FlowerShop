import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ApiError, verifyEmail } from "../api/authApi";

type VerifyStatus = "idle" | "loading" | "success" | "error";

function extractToken(search: string): string | null {
  const params = new URLSearchParams(search);
  const fromNamedParam = params.get("token");

  if (fromNamedParam) {
    return fromNamedParam;
  }

  const raw = search.startsWith("?") ? search.slice(1) : search;
  if (!raw) {
    return null;
  }

  try {
    return decodeURIComponent(raw);
  } catch {
    return raw;
  }
}

export default function VerifyEmail() {
  const { search } = useLocation();
  const token = useMemo(() => extractToken(search), [search]);

  const [status, setStatus] = useState<VerifyStatus>("idle");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Токен подтверждения не найден в ссылке.");
      return;
    }

    let isActive = true;

    (async () => {
      setStatus("loading");
      try {
        await verifyEmail(token);
        if (!isActive) {
          return;
        }
        setStatus("success");
        setMessage("Почта успешно подтверждена. Теперь можно войти.");
      } catch (error) {
        if (!isActive) {
          return;
        }
        setStatus("error");
        setMessage(
          error instanceof ApiError ? error.message : "Не удалось подтвердить почту.",
        );
      }
    })();

    return () => {
      isActive = false;
    };
  }, [token]);

  return (
    <section className="mx-auto mt-10 w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="mb-4 text-2xl font-bold">Подтверждение почты</h1>

      {status === "loading" ? (
        <p className="rounded bg-blue-100 p-3 text-sm text-blue-800">
          Подтверждаем вашу почту...
        </p>
      ) : null}

      {status === "success" ? (
        <p className="rounded bg-green-100 p-3 text-sm text-green-800">{message}</p>
      ) : null}

      {status === "error" ? (
        <p className="rounded bg-red-100 p-3 text-sm text-red-800">{message}</p>
      ) : null}

      <div className="mt-6 flex gap-3">
        <Link
          to="/login"
          className="rounded bg-yellow-500 px-4 py-2 font-semibold text-black"
        >
          Перейти к входу
        </Link>
        <Link
          to="/register"
          className="rounded border border-gray-500 px-4 py-2 font-semibold"
        >
          Зарегистрироваться снова
        </Link>
      </div>
    </section>
  );
}
