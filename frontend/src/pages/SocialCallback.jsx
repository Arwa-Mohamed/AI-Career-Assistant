import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { exchangeSocialLoginCode } from "../services/api";
import { useAuth } from "../context/AuthContext";

function SocialCallback() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [error, setError] = useState("");
  const [processing, setProcessing] =
    useState(true);

  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) {
      return;
    }

    hasProcessed.current = true;

    const completeLogin = async () => {
      try {
        setProcessing(true);
        setError("");

        const params = new URLSearchParams(
          window.location.search
        );

        const code = params.get("code");
        const oauthError =
          params.get("error");
        const oauthErrorDescription =
          params.get("error_description");

        /* =====================================================
           OAUTH ERROR
           ===================================================== */

        if (oauthError) {
          throw new Error(
            oauthErrorDescription ||
              "Social login was cancelled or rejected."
          );
        }

        /* =====================================================
           MISSING CODE
           ===================================================== */

        if (!code) {
          throw new Error(
            "Social login code is missing. Please try again."
          );
        }

        /* =====================================================
           EXCHANGE CODE FOR JWT
           ===================================================== */

        const data =
          await exchangeSocialLoginCode(code);

        if (
          !data?.access ||
          !data?.refresh
        ) {
          throw new Error(
            "Invalid social login response. Authentication tokens were not received."
          );
        }

        /* =====================================================
           STORE AUTHENTICATION
           ===================================================== */

        login(
          data.access,
          data.refresh
        );

        /* =====================================================
           CLEAN OAUTH QUERY PARAMETERS
           ===================================================== */

        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );

        /* =====================================================
           REDIRECT
           ===================================================== */

        navigate(
          "/dashboard",
          {
            replace: true,
          }
        );
      } catch (err) {
        setError(
          err?.message ||
            "Social login failed. Please try again."
        );
      } finally {
        setProcessing(false);
      }
    };

    completeLogin();
  }, [login, navigate]);

  /* =========================================================
     ERROR STATE
     ========================================================= */

  if (error) {
    return (
      <div className="auth-page">
        <div className="auth-card social-callback-card">
          <div className="social-callback-icon error">
            !
          </div>

          <div className="auth-heading">
            <span className="auth-kicker">
              AUTHENTICATION
            </span>

            <h2>
              Login Failed
            </h2>

            <p>
              We couldn't complete your
              social login.
            </p>
          </div>

          <div
            className="auth-alert auth-alert-error"
            role="alert"
          >
            <span className="auth-alert-icon">
              !
            </span>

            <div>
              <strong>
                Authentication error
              </strong>

              <p>
                {error}
              </p>
            </div>
          </div>

          <button
            className="auth-button"
            type="button"
            onClick={() =>
              navigate(
                "/login",
                {
                  replace: true,
                }
              )
            }
          >
            Back to Login
            <span className="auth-button-arrow">
              →
            </span>
          </button>
        </div>
      </div>
    );
  }

  /* =========================================================
     LOADING STATE
     ========================================================= */

  if (processing) {
    return (
      <div className="auth-page">
        <div className="auth-card social-callback-card">
          <div className="social-callback-icon">
            AI
          </div>

          <div className="auth-heading">
            <span className="auth-kicker">
              AUTHENTICATION
            </span>

            <h2>
              Completing your login...
            </h2>

            <p>
              Please wait while we securely
              finish signing you in.
            </p>
          </div>

          <div className="social-callback-loading">
            <div className="social-callback-spinner" />

            <span>
              Verifying your account
            </span>
          </div>

          <div className="social-callback-note">
            Please don't close or refresh this
            page.
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default SocialCallback;