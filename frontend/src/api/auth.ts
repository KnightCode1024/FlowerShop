import api from './axios';

interface LoginResponse {
    id: number;
    email: string;
    username: string;
  };
}

export const authApi = {
    register: (email: string, username: string, password: string) =>
    api.post<>

    login: (email: string, password: string) => 
    api.post<LoginResponse>('/users/login', { email, password }),

    verifyOTP: (code: string) => 
    api.post<{ user: any }>('users/verify-otp', { code }),

    getProfile: () => 
    api.get('/users/me'),

    logout: () => 
    api.post('/users/logout')
};