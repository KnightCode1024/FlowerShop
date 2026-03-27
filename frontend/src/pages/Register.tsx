import {FormEvent, useState} from "react";
import {Link, useNavigate} from "react-router-dom";
import {ApiError} from "../api/authApi";
import {useAuth} from "../auth/useAuth";

export default function Register() {
    const navigate = useNavigate();
    const {register} = useAuth();

    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setError(null);
        setSuccess(null);
        setIsSubmitting(true);

        try {
            await register({email, username, password});
            setSuccess("Регистрация завершена. Подтвердите почту и войдите.");
            setTimeout(() => navigate("/login"), 1200);
        } catch (err) {
            setError(err instanceof ApiError ? err.message : "Не удалось зарегистрироваться");
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <section className="mx-auto mt-10 w-full max-w-md rounded-xl border border-slate-200 p-6 shadow-sm">
            <h1 className="mb-6 text-2xl font-bold">Регистрация</h1>

            {error ? (
                <p className="mb-4 rounded bg-red-100 p-3 text-sm text-red-800">{error}</p>
            ) : null}

            {success ? (
                <p className="mb-4 rounded bg-green-100 p-3 text-sm text-green-800">
                    {success}
                </p>
            ) : null}

            <form onSubmit={onSubmit} className="flex flex-col gap-4">
                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Эл. почта</span>
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-3 py-2"
                        placeholder="you@example.com"
                    />
                </label>

                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Имя пользователя</span>
                    <input
                        type="text"
                        required
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-3 py-2"
                        placeholder="имя пользователя"
                    />
                </label>

                <label className="flex flex-col gap-1">
                    <span className="text-sm text-slate-600">Пароль</span>
                    <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-3 py-2"
                        placeholder="Пароль"
                    />
                </label>

                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="rounded bg-yellow-500 px-4 py-2 font-semibold text-black disabled:opacity-60"
                >
                    {isSubmitting ? "Создаем..." : "Создать аккаунт"}
                </button>
            </form>

            <p className="mt-4 text-sm text-gray-400">
                Уже зарегистрированы?{" "}
                <Link to="/login" className="text-yellow-400 underline">
                    Войти
                </Link>
            </p>
        </section>
    );
}
