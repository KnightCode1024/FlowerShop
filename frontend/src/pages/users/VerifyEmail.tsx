import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";

const VerifyEmail: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setErrorMessage] = useState<string>('');

    useEffect(() => {
        const verifyEmail = async () => {
            const token = searchParams.get('token');

            if (!token) {
                setStatus('error');
                setErrorMessage('Токен верификации не найден');
                return;
            }

            try {
                const response = await axios.get<boolean>(
                    `http://127.0.0.1:8000/api/users/verify-email?token=${token}`
                );
                
                if (response.data === true) {
                    setStatus('success');
                    setTimeout(() => {
                        navigate('/login');
                    }, 3000);
                } else {
                    setStatus('error');
                    setErrorMessage("Не удалось подтвердить email");
                }
            } catch (error) {
                setStatus('error');
                if (axios.isAxiosError(error)) {
                    if (error.response) {
                        if (typeof error.response.data === 'string') {
                            setErrorMessage(error.response.data);
                        } else if (error.response.data?.message) {
                            setErrorMessage(error.response.data.message);
                        } else {
                            setErrorMessage(`Ошибка сервера: ${error.response.status}`);
                        }
                    } else if (error.code === 'ECONNABORTED') {
                        setErrorMessage('Превышено время ожидания ответа от сервера');
                    } else if (error.request) {
                        setErrorMessage('Сервер не отвечает. Проверьте подключение');
                    } else {
                        setErrorMessage('Произошла ошибка при отправке запроса');
                    }
                } else {
                    setErrorMessage('Неизвестная ошибка');
                }
            }
        };

        verifyEmail();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen bg-white flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                {status === 'loading' && (
                    <div className="text-center">
                        <div className="flex justify-center mb-8">
                            <div className="w-12 h-12 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin"></div>
                        </div>
                        <h2 className="text-2xl font-light text-gray-900 mb-3">
                            Подтверждение email
                        </h2>
                        <p className="text-gray-500 text-sm">
                            Пожалуйста, подождите, идет проверка...
                        </p>
                    </div>
                )}

                {status === 'success' && (
                    <div className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center">
                                <svg className="w-8 h-8 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                        </div>
                        <h2 className="text-2xl font-light text-gray-900 mb-3">
                            Email подтвержден
                        </h2>
                        <p className="text-gray-500 text-sm mb-6">
                            Ваш email успешно верифицирован
                        </p>
                        <p className="text-xs text-gray-400 mb-8">
                            Перенаправление на страницу входа через несколько секунд...
                        </p>
                        <button 
                            onClick={() => navigate('/login')}
                            className="w-full bg-gray-900 text-white py-3 px-4 text-sm font-medium hover:bg-gray-800 transition-colors"
                        >
                            Перейти на страницу входа
                        </button>
                    </div>
                )}

                {status === 'error' && (
                    <div className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center">
                                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </div>
                        </div>
                        <h2 className="text-2xl font-light text-gray-900 mb-3">
                            Ошибка верификации
                        </h2>
                        <p className="text-gray-500 text-sm mb-8">
                            {message}
                        </p>
                        <div className="space-y-3">
                            <button 
                                onClick={() => window.location.reload()}
                                className="w-full bg-gray-900 text-white py-3 px-4 text-sm font-medium hover:bg-gray-800 transition-colors"
                            >
                                Попробовать снова
                            </button>
                            <button 
                                onClick={() => navigate('/')}
                                className="w-full bg-white text-gray-900 py-3 px-4 text-sm font-medium border border-gray-200 hover:bg-gray-50 transition-colors"
                            >
                                На главную
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VerifyEmail;