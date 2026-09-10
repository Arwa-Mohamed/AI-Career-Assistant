import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginUser } from "../services/api";
import { useAuth } from "../context/AuthContext";

import "./Auth.css";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState("");

  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  const usernameError = fieldErrors.username;
  const passwordError = fieldErrors.password;

  const isBusy = loading || Boolean(socialLoading);

  const canSubmit = useMemo(() => {
    return (
      username.trim().length > 0 &&
      password.length > 0 &&
      !isBusy
    );
  }, [username, password, isBusy]);

  /* =========================================================
     VALIDATION
  ========================================================= */

  const validateForm = () => {
    const errors = {};

    if (!username.trim()) {
      errors.username = "Please enter your username.";
    } else if (username.trim().length < 3) {
      errors.username =
        "Username must be at least 3 characters.";
    }

    if (!password) {
      errors.password = "Please enter your password.";
    }

    setFieldErrors(errors);

    return Object.keys(errors).length === 0;
  };

  const clearFieldError = (field) => {
    setFieldErrors((previous) => {
      if (!previous[field]) {
        return previous;
      }

      const updated = { ...previous };
      delete updated[field];

      return updated;
    });
  };

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);

    clearFieldError("username");
    setError("");
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);

    clearFieldError("password");
    setError("");
  };

  /* =========================================================
     LOGIN
  ========================================================= */

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      const data = await loginUser(
        username.trim(),
        password
      );

      if (!data?.access || !data?.refresh) {
        throw new Error(
          "Login response does not contain valid authentication tokens."
        );
      }

      login(
        data.access,
        data.refresh
      );

      navigate("/dashboard");
    } catch (err) {
      const message =
        err?.message ||
        "Login failed. Please check your credentials and try again.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     SOCIAL LOGIN
  ========================================================= */

  const handleSocialLogin = (provider) => {
    setError("");
    setFieldErrors({});
    setSocialLoading(provider);

    const apiUrl =
      import.meta.env.VITE_API_URL ||
      "http://127.0.0.1:8000";

    window.location.href =
      `${apiUrl}/accounts/${provider}/login/`;
  };

  /* =========================================================
     FORGOT PASSWORD
  ========================================================= */

  const handleForgotPassword = () => {
    setError("");
    setFieldErrors({});

    navigate("/forgot-password");
  };

  /* =========================================================
     JSX
  ========================================================= */

  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* ===================================================
            BRAND
        =================================================== */}

        <div className="auth-brand">
          <div className="auth-logo">
            AI
          </div>

          <div>
            <h1>Career Assistant</h1>

            <p>
              AI-powered career guidance
            </p>
          </div>
        </div>

        {/* ===================================================
            HEADING
        =================================================== */}

        <div className="auth-heading">
          <span className="auth-kicker">
            WELCOME BACK
          </span>

          <h2>
            Welcome 👋
          </h2>

          <p>
            Sign in to continue your
            personalized career journey.
          </p>
        </div>

        {/* ===================================================
            ERROR
        =================================================== */}

        {error && (
          <div
            className="auth-alert auth-alert-error"
            role="alert"
            aria-live="polite"
          >
            <span className="auth-alert-icon">
              !
            </span>

            <div>
              <strong>
                Sign in unsuccessful
              </strong>

              <p>
                {error}
              </p>
            </div>
          </div>
        )}

        {/* ===================================================
            FORM
        =================================================== */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
          noValidate
        >

          {/* =================================================
              USERNAME
          ================================================= */}

          <div
            className={`auth-field ${
              usernameError
                ? "has-error"
                : ""
            }`}
          >
            <div className="auth-label-row">
              <label htmlFor="login-username">
                Username
              </label>
            </div>

            <div className="auth-input-wrapper">
              <span
                className="auth-input-icon"
                aria-hidden="true"
              >
                @
              </span>

              <input
                id="login-username"
                name="username"
                type="text"
                value={username}
                onChange={handleUsernameChange}
                placeholder="Enter your username"
                autoComplete="username"
                disabled={isBusy}
                aria-invalid={Boolean(usernameError)}
                aria-describedby={
                  usernameError
                    ? "login-username-error"
                    : undefined
                }
                required
              />
            </div>

            {usernameError && (
              <span
                id="login-username-error"
                className="field-error"
              >
                {usernameError}
              </span>
            )}
          </div>

          {/* =================================================
              PASSWORD
          ================================================= */}

          <div
            className={`auth-field ${
              passwordError
                ? "has-error"
                : ""
            }`}
          >
            <div className="auth-label-row">
              <label htmlFor="login-password">
                Password
              </label>

              <button
                type="button"
                className="forgot-password-link"
                onClick={handleForgotPassword}
                disabled={isBusy}
              >
                Forgot Password?
              </button>
            </div>

            <div className="password-wrapper">
              <span
                className="auth-input-icon"
                aria-hidden="true"
              >
                •
              </span>

              <input
                id="login-password"
                name="password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                value={password}
                onChange={handlePasswordChange}
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={isBusy}
                aria-invalid={Boolean(passwordError)}
                aria-describedby={
                  passwordError
                    ? "login-password-error"
                    : undefined
                }
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(
                    (previous) => !previous
                  )
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                disabled={isBusy}
              >
                {showPassword
                  ? "Hide"
                  : "Show"}
              </button>
            </div>

            {passwordError && (
              <span
                id="login-password-error"
                className="field-error"
              >
                {passwordError}
              </span>
            )}
          </div>

          {/* =================================================
              SUBMIT
          ================================================= */}

          <button
            className="auth-button"
            type="submit"
            disabled={!canSubmit}
          >
            {loading ? (
              <>
                <span
                  className="auth-button-spinner"
                  aria-hidden="true"
                />

                Signing in...
              </>
            ) : (
              <>
                Sign In

                <span
                  className="auth-button-arrow"
                  aria-hidden="true"
                >
                  →
                </span>
              </>
            )}
          </button>
        </form>

        {/* ===================================================
            DIVIDER
        =================================================== */}

        <div className="auth-divider">
          <span>
            OR CONTINUE WITH
          </span>
        </div>

        {/* ===================================================
            SOCIAL LOGIN
        =================================================== */}

        <div className="social-buttons">

          {/* GOOGLE */}

          <button
            type="button"
            className="social-button"
            onClick={() =>
              handleSocialLogin("google")
            }
            disabled={isBusy}
          >
            <span className="social-icon google-icon">
              G
            </span>

            <span>
              {socialLoading === "google"
                ? "Connecting..."
                : "Continue with Google"}
            </span>

            {socialLoading === "google" && (
              <span
                className="social-spinner"
                aria-hidden="true"
              />
            )}
          </button>

          {/* GITHUB */}

          <button
            type="button"
            className="social-button"
            onClick={() =>
              handleSocialLogin("github")
            }
            disabled={isBusy}
          >
            <span className="social-icon github-icon">
              Git
            </span>

            <span>
              {socialLoading === "github"
                ? "Connecting..."
                : "Continue with GitHub"}
            </span>

            {socialLoading === "github" && (
              <span
                className="social-spinner"
                aria-hidden="true"
              />
            )}
          </button>
        </div>

        {/* ===================================================
            FOOTER
        =================================================== */}

        <div className="auth-footer">
          <span>
            Don't have an account?
          </span>

          <button
            type="button"
            onClick={() =>
              navigate("/register")
            }
            disabled={isBusy}
          >
            Create Account
          </button>
        </div>

      </div>
    </div>
  );
}

export default Login;