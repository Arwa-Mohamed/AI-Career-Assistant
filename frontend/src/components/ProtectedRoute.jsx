import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children }) {
  const location = useLocation();

  const {
    isAuthenticated,
    authReady,
  } = useAuth();

  /*
   * Wait until the initial authentication state
   * has been restored from localStorage.
   */
  if (!authReady) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f7f8fa",
          color: "#1f2937",
          fontFamily:
            "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        }}
      >
        <div
          style={{
            textAlign: "center",
            padding: "32px",
          }}
        >
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "50%",
              border: "4px solid #e5e7eb",
              borderTopColor: "#2563eb",
              margin: "0 auto 16px",
              animation:
                "protected-route-spin 0.8s linear infinite",
            }}
          />

          <strong
            style={{
              display: "block",
              fontSize: "16px",
              marginBottom: "6px",
            }}
          >
            Restoring your session...
          </strong>

          <span
            style={{
              display: "block",
              fontSize: "13px",
              color: "#6b7280",
            }}
          >
            Checking your authentication state.
          </span>

          <style>
            {`
              @keyframes protected-route-spin {
                from {
                  transform: rotate(0deg);
                }

                to {
                  transform: rotate(360deg);
                }
              }
            `}
          </style>
        </div>
      </div>
    );
  }

  /*
   * After initialization, redirect unauthenticated users
   * to the login page.
   */
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    );
  }

  return children;
}

export default ProtectedRoute;