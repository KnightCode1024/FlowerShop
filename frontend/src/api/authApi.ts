export interface ApiErrorPayload {
  detail?: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  role: string;
}

export interface AccessTokenResponse {
  access_token: string;
}

export interface TokenPairResponse {
  access_token: string;
  refresh_token: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RefreshPayload {
  refresh_token?: string;
}

export interface OtpPayload {
  otp_code: string;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000/api";

async function request<T>(
  path: string,
  init?: RequestInit,
  accessToken?: string,
): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body) {
    headers.set("Content-Type", "application/json");
  }

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as ApiErrorPayload;
    throw new ApiError(data.detail ?? "Ошибка запроса", response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function registerUser(payload: RegisterPayload): Promise<UserResponse> {
  return request<UserResponse>("/users/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload: LoginPayload): Promise<AccessTokenResponse> {
  return request<AccessTokenResponse>("/users/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function checkOtpCode(
  payload: OtpPayload,
  accessToken: string,
): Promise<TokenPairResponse> {
  return request<TokenPairResponse>(
    "/users/check-code",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    accessToken,
  );
}

export function refreshUserToken(
  payload?: RefreshPayload,
): Promise<TokenPairResponse> {
  return request<TokenPairResponse>("/users/refresh", {
    method: "POST",
    body: payload ? JSON.stringify(payload) : undefined,
  });
}

export function getProfile(): Promise<UserResponse> {
  return request<UserResponse>("/users/me", { method: "GET" });
}

export function verifyEmail(token: string): Promise<boolean> {
  const encodedToken = encodeURIComponent(token);
  return request<boolean>(`/users/verify-email?token=${encodedToken}`, {
    method: "GET",
  });
}

export function resendOtpCode(accessToken: string): Promise<boolean> {
  return request<boolean>("/users/resend-otp", { method: "POST" }, accessToken);
}

export function logoutUser(): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>("/users/logout", { method: "POST" });
}
