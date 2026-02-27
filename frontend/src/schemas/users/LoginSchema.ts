import {z} from 'zod';

export const loginSchema = z.object(
    {
    email: z
        .string()
        .min(1, 'Email обязателен'),
    password: z
        .string()
        .min(1, 'Пароль обязателен')
        .min(6, 'Пароль должен содержать минимум 6 символов'),
        }
)

export type LoginFromData = z.infer<typeof loginSchema>;