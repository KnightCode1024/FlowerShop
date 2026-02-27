// components/LoginForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '../schemas/loginSchema';

export const LoginForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
    mode: 'onBlur', // Валидация при потере фокуса
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      // Имитация отправки на сервер
      console.log('Данные формы:', data);
      
      // Здесь будет ваш API запрос
      // await loginApi(data);
      
      alert('Форма успешно отправлена!');
    } catch (error) {
      console.error('Ошибка при отправке:', error);
      alert('Произошла ошибка при входе');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="login-form">
      <h2>Вход в систему</h2>
      
      {/* Поле Email */}
      <div className="form-group">
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className={errors.email ? 'error' : ''}
          placeholder="example@mail.com"
        />
        {errors.email && (
          <span className="error-message">{errors.email.message}</span>
        )}
      </div>

      {/* Поле Пароль */}
      <div className="form-group">
        <label htmlFor="password">Пароль:</label>
        <input
          id="password"
          type="password"
          {...register('password')}
          className={errors.password ? 'error' : ''}
          placeholder="Минимум 6 символов"
        />
        {errors.password && (
          <span className="error-message">{errors.password.message}</span>
        )}
      </div>

      {/* Кнопка отправки */}
      <button 
        type="submit" 
        disabled={isSubmitting || !isValid}
        className={isSubmitting ? 'loading' : ''}
      >
        {isSubmitting ? 'Вход...' : 'Войти'}
      </button>
    </form>
  );
};