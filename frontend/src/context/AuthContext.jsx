import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  /*
   * Read the token immediately on startup.
   * This prevents a protected route from redirecting to
   * login before authentication state has been restored.
   */
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const accessToken =
      localStorage.getItem("accessToken");

    return Boolean(accessToken);
  });

  /*
   * Tells protected routes whether the initial auth check
   * has completed.
   */
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const accessToken =
      localStorage.getItem("accessToken");

    const refreshToken =
      localStorage.getItem("refreshToken");

    /*
     * Authentication is considered valid when an access token
     * exists. The refresh token is kept separately for API
     * token renewal.
     */
    setIsAuthenticated(Boolean(accessToken));

    /*
     * The initial authentication state is now restored.
     */
    setAuthReady(true);

    /*
     * If the access token does not exist, keep auth state false.
     * We intentionally do not clear the refresh token here because
     * the API layer may use it to recover an expired access token.
     */
    if (!accessToken && !refreshToken) {
      setIsAuthenticated(false);
    }
  }, []);

  /*
   * Login
   */
  const login = (accessToken, refreshToken) => {
    if (!accessToken) {
      throw new Error(
        "A valid access token is required."
      );
    }

    localStorage.setItem(
      "accessToken",
      accessToken
    );

    if (refreshToken) {
      localStorage.setItem(
        "refreshToken",
        refreshToken
      );
    }

    setIsAuthenticated(true);
    setAuthReady(true);
  };

  /*
   * Logout
   */
  const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");

    setIsAuthenticated(false);
    setAuthReady(true);
  };

  /*
   * Used by API refresh logic or future auth features.
   */
  const updateAccessToken = (accessToken) => {
    if (!accessToken) {
      return;
    }

    localStorage.setItem(
      "accessToken",
      accessToken
    );

    setIsAuthenticated(true);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        authReady,
        login,
        logout,
        updateAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}