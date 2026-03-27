import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import {
  ApiError,
  checkOtpCode,
  getProfile,
  loginUser,
  logoutUser,
  refreshUserToken,
  resendOtpCode,
  registerUser,
  type UserResponse,
} from "../api/authApi";

type Nullable<T> = T | null;

interface RegisterInput {
  email: string;
  username: string;
  password: string;
}

interface LoginInput {
  email: string;
  password: string;
}

interface AuthContextValue {
  user: Nullable<UserResponse>;
  isLoading: boolean;
  isAuthenticated: boolean;
  otpEmail: Nullable<string>;
  isOtpPending: boolean;
  register: (input: RegisterInput) => Promise<void>;
  loginStart: (input: LoginInput) => Promise<void>;
  submitOtp: (otpCode: string) => Promise<void>;
  resendOtp: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Nullable<UserResponse>>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [otpPendingToken, setOtpPendingToken] = useState<Nullable<string>>(null);
  const [otpEmail, setOtpEmail] = useState<Nullable<string>>(null);

  const refreshPromiseRef = useRef<Promise<void> | null>(null);

  const logout = useCallback(() => {
    void logoutUser().catch(() => undefined);
    setUser(null);
    setOtpPendingToken(null);
    setOtpEmail(null);
  }, []);

  const runRefresh = useCallback(async (): Promise<void> => {
    if (!refreshPromiseRef.current) {
      refreshPromiseRef.current = (async () => {
        await refreshUserToken();
      })().finally(() => {
        refreshPromiseRef.current = null;
      });
    }

    await refreshPromiseRef.current;
  }, []);

  const loadProfile = useCallback(
    async (tryRefresh = true) => {
      try {
        const profile = await getProfile();
        setUser(profile);
      } catch (error) {
        if (tryRefresh && error instanceof ApiError && error.status === 401) {
          await runRefresh();
          const profile = await getProfile();
          setUser(profile);
          return;
        }
        throw error;
      }
    },
    [runRefresh],
  );

  const refreshProfile = useCallback(async () => {
    await loadProfile(true);
  }, [loadProfile]);

  const register = useCallback(async (input: RegisterInput) => {
    await registerUser(input);
  }, []);

  const loginStart = useCallback(async (input: LoginInput) => {
    const data = await loginUser(input);
    setOtpPendingToken(data.access_token);
    setOtpEmail(input.email);
  }, []);

  const submitOtp = useCallback(
    async (otpCode: string) => {
      if (!otpPendingToken) {
        throw new ApiError("Сессия OTP не найдена. Войдите еще раз.", 400);
      }

      await checkOtpCode({ otp_code: otpCode }, otpPendingToken);
      setOtpPendingToken(null);
      setOtpEmail(null);
      await loadProfile(false);
    },
    [loadProfile, otpPendingToken],
  );

  const resendOtp = useCallback(async () => {
    if (!otpPendingToken) {
      throw new ApiError("Сессия OTP не найдена. Войдите еще раз.", 400);
    }
    await resendOtpCode(otpPendingToken);
  }, [otpPendingToken]);

  useEffect(() => {
    let isMounted = true;

    (async () => {
      try {
        await loadProfile(true);
      } catch {
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    })();

    return () => {
      isMounted = false;
    };
  }, [loadProfile]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      otpEmail,
      isOtpPending: Boolean(otpPendingToken),
      register,
      loginStart,
      submitOtp,
      resendOtp,
      refreshProfile,
      logout,
    }),
    [
      isLoading,
      loginStart,
      logout,
      otpEmail,
      otpPendingToken,
      refreshProfile,
      register,
      resendOtp,
      submitOtp,
      user,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth должен использоваться внутри AuthProvider");
  }
  return context;
}
