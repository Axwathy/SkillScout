"use client";

import React, { createContext, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User, AuthState } from "@/types/auth";
import { getMe, login as apiLogin, logout as apiLogout } from "@/lib/auth";
import { ApiError } from "@/lib/api";

interface AuthContextType extends AuthState {
  login: (credentials: Record<string, string>) => Promise<User | null>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<User | null>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  });

  const refreshSession = useCallback(async (): Promise<User | null> => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      const user = await getMe();
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
      return user;
    } catch (err: any) {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      return null;
    }
  }, []);

  useEffect(() => {
    const handleSessionExpired = () => {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: "Your session has expired. Please sign in again.",
      });

      const path = window.location.pathname;
      if (path.startsWith("/candidate")) {
        router.push("/login");
      } else if (path.startsWith("/dashboard")) {
        router.push("/login");
      }
    };

    window.addEventListener("auth:session-expired", handleSessionExpired);
    return () => window.removeEventListener("auth:session-expired", handleSessionExpired);
  }, [router]);

  const login = async (credentials: Record<string, string>): Promise<User | null> => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      await apiLogin(credentials);
      return await refreshSession();
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof ApiError ? err.data.detail : "Login failed.",
      }));
      throw err;
    }
  };

  const logout = async () => {
    try {
      setState((prev) => ({ ...prev, isLoading: true }));
      await apiLogout();
    } catch (err) {
      console.error("Logout error", err);
    } finally {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        refreshSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
