// Запросы
export interface LoginData {
  email: string;
  password: string;
}

export interface OTPData {
  otp_code: string;
}

// Ответы
export interface LoginResponse {
  message: string; // "check your code on email."
  access_token?: string; // временный токен для 2FA
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: 'user' | 'employee' | 'admin';
}

// Состояние 2FA
export interface TwoFAState {
  requires_2fa: boolean;
  email?: string;
  password?: string;
}