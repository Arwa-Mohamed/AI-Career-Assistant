import {
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import { registerUser } from "../services/api";

import "./Auth.css";

function Register() {
  const navigate = useNavigate();

  const [username, setUsername] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [password2, setPassword2] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [showPassword2, setShowPassword2] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [fieldErrors, setFieldErrors] =
    useState({});

  /* =========================================================
     PASSWORD STRENGTH
     ========================================================= */

  const passwordStrength = useMemo(() => {
    if (!password) {
      return {
        score: 0,
        label: "",
        className: "empty",
      };
    }

    let score = 0;

    if (password.length >= 8) {
      score += 1;
    }

    if (password.length >= 12) {
      score += 1;
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    }

    if (/[0-9]/.test(password)) {
      score += 1;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
      score += 1;
    }

    if (score <= 2) {
      return {
        score,
        label: "Weak",
        className: "weak",
      };
    }

    if (score <= 4) {
      return {
        score,
        label: "Medium",
        className: "medium",
      };
    }

    return {
      score,
      label: "Strong",
      className: "strong",
    };
  }, [password]);

  /* =========================================================
     PASSWORD REQUIREMENTS
     ========================================================= */

  const passwordRequirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
  };

  /* =========================================================
     FORM VALIDATION
     ========================================================= */

  const validateForm = () => {
    const errors = {};

    const trimmedUsername =
      username.trim();

    const trimmedEmail =
      email.trim();

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!trimmedUsername) {
      errors.username =
        "Please enter a username.";
    } else if (
      trimmedUsername.length < 3
    ) {
      errors.username =
        "Username must be at least 3 characters.";
    } else if (
      trimmedUsername.length > 30
    ) {
      errors.username =
        "Username must be 30 characters or less.";
    }

    if (!trimmedEmail) {
      errors.email =
        "Please enter your email.";
    } else if (
      !emailPattern.test(trimmedEmail)
    ) {
      errors.email =
        "Please enter a valid email address.";
    }

    if (!password) {
      errors.password =
        "Please enter a password.";
    } else if (
      password.length < 8
    ) {
      errors.password =
        "Password must be at least 8 characters.";
    }

    if (!password2) {
      errors.password2 =
        "Please confirm your password.";
    } else if (
      password !== password2
    ) {
      errors.password2 =
        "Passwords do not match.";
    }

    setFieldErrors(errors);

    return Object.keys(errors).length === 0;
  };

  const clearFieldError = (field) => {
    setFieldErrors((prev) => {
      if (!prev[field]) {
        return prev;
      }

      const updated = {
        ...prev,
      };

      delete updated[field];

      return updated;
    });
  };

  /* =========================================================
     SUBMIT
     ========================================================= */

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      await registerUser(
        username.trim(),
        email.trim(),
        password,
        password2
      );

      setMessage(
        "Account created successfully! Redirecting to login..."
      );

      setUsername("");
      setEmail("");
      setPassword("");
      setPassword2("");
      setFieldErrors({});

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (err) {
      const serverMessage =
        err?.message ||
        "Registration failed. Please try again.";

      setError(serverMessage);
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     LIVE PASSWORD MATCH
     ========================================================= */

  const passwordMismatch =
    password2.length > 0 &&
    password !== password2;

  const passwordMatch =
    password2.length > 0 &&
    password === password2;

  return (
    <div className="auth-page">
      <div className="auth-card auth-register-card">
        {/* BRAND */}

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

        {/* HEADING */}

        <div className="auth-heading">
          <span className="auth-kicker">
            GET STARTED
          </span>

          <h2>
            Create your account 🚀
          </h2>

          <p>
            Build your profile, analyze your
            career path, and prepare for your
            next opportunity.
          </p>
        </div>

        {/* ERROR */}

        {error && (
          <div
            className="auth-alert auth-alert-error"
            role="alert"
          >
            <span className="auth-alert-icon">
              !
            </span>

            <div>
              <strong>
                Registration unsuccessful
              </strong>

              <p>{error}</p>
            </div>
          </div>
        )}

        {/* SUCCESS */}

        {message && (
          <div
            className="auth-alert auth-alert-success"
            role="status"
          >
            <span className="auth-alert-icon">
              ✓
            </span>

            <div>
              <strong>
                Account created
              </strong>

              <p>{message}</p>
            </div>
          </div>
        )}

        {/* FORM */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
          noValidate
        >
          {/* USERNAME */}

          <div
            className={`auth-field ${
              fieldErrors.username
                ? "has-error"
                : ""
            }`}
          >
            <label htmlFor="register-username">
              Username
            </label>

            <div className="auth-input-wrapper">
              <span className="auth-input-icon">
                @
              </span>

              <input
                id="register-username"
                type="text"
                value={username}
                onChange={(e) => {
                  setUsername(
                    e.target.value
                  );
                  clearFieldError(
                    "username"
                  );
                  setError("");
                }}
                placeholder="Choose a username"
                maxLength={30}
                disabled={loading}
                autoComplete="username"
                aria-invalid={
                  !!fieldErrors.username
                }
                aria-describedby={
                  fieldErrors.username
                    ? "register-username-error"
                    : undefined
                }
                required
              />
            </div>

            <div className="field-meta">
              {fieldErrors.username ? (
                <span
                  id="register-username-error"
                  className="field-error"
                >
                  {fieldErrors.username}
                </span>
              ) : (
                <span className="field-hint">
                  3–30 characters
                </span>
              )}

              <span className="field-counter">
                {username.length}/30
              </span>
            </div>
          </div>

          {/* EMAIL */}

          <div
            className={`auth-field ${
              fieldErrors.email
                ? "has-error"
                : ""
            }`}
          >
            <label htmlFor="register-email">
              Email
            </label>

            <div className="auth-input-wrapper">
              <span className="auth-input-icon">
                @
              </span>

              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(
                    e.target.value
                  );
                  clearFieldError(
                    "email"
                  );
                  setError("");
                }}
                placeholder="you@example.com"
                disabled={loading}
                autoComplete="email"
                aria-invalid={
                  !!fieldErrors.email
                }
                aria-describedby={
                  fieldErrors.email
                    ? "register-email-error"
                    : undefined
                }
                required
              />
            </div>

            {fieldErrors.email && (
              <span
                id="register-email-error"
                className="field-error"
              >
                {fieldErrors.email}
              </span>
            )}
          </div>

          {/* PASSWORD */}

          <div
            className={`auth-field ${
              fieldErrors.password
                ? "has-error"
                : ""
            }`}
          >
            <label htmlFor="register-password">
              Password
            </label>

            <div className="password-wrapper">
              <span className="auth-input-icon">
                •
              </span>

              <input
                id="register-password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                value={password}
                onChange={(e) => {
                  setPassword(
                    e.target.value
                  );
                  clearFieldError(
                    "password"
                  );
                  setError("");
                }}
                placeholder="Create a strong password"
                disabled={loading}
                autoComplete="new-password"
                aria-invalid={
                  !!fieldErrors.password
                }
                aria-describedby={
                  fieldErrors.password
                    ? "register-password-error"
                    : undefined
                }
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(
                    (prev) => !prev
                  )
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                disabled={loading}
              >
                {showPassword
                  ? "Hide"
                  : "Show"}
              </button>
            </div>

            {/* PASSWORD STRENGTH */}

            {password && (
              <div className="password-strength">
                <div className="strength-header">
                  <span>
                    Password strength
                  </span>

                  <strong
                    className={`strength-label ${passwordStrength.className}`}
                  >
                    {
                      passwordStrength.label
                    }
                  </strong>
                </div>

                <div className="strength-bars">
                  {[1, 2, 3, 4, 5, 6].map(
                    (bar) => (
                      <span
                        key={bar}
                        className={
                          bar <=
                          passwordStrength.score
                            ? `active ${passwordStrength.className}`
                            : ""
                        }
                      />
                    )
                  )}
                </div>

                <div className="password-rules">
                  <span
                    className={
                      passwordRequirements.length
                        ? "valid"
                        : ""
                    }
                  >
                    ✓ 8+ characters
                  </span>

                  <span
                    className={
                      passwordRequirements.uppercase
                        ? "valid"
                        : ""
                    }
                  >
                    ✓ Uppercase
                  </span>

                  <span
                    className={
                      passwordRequirements.lowercase
                        ? "valid"
                        : ""
                    }
                  >
                    ✓ Lowercase
                  </span>

                  <span
                    className={
                      passwordRequirements.number
                        ? "valid"
                        : ""
                    }
                  >
                    ✓ Number
                  </span>
                </div>
              </div>
            )}

            {fieldErrors.password && (
              <span
                id="register-password-error"
                className="field-error"
              >
                {fieldErrors.password}
              </span>
            )}
          </div>

          {/* CONFIRM PASSWORD */}

          <div
            className={`auth-field ${
              fieldErrors.password2 ||
              passwordMismatch
                ? "has-error"
                : ""
            }`}
          >
            <label htmlFor="register-password2">
              Confirm Password
            </label>

            <div className="password-wrapper">
              <span className="auth-input-icon">
                •
              </span>

              <input
                id="register-password2"
                type={
                  showPassword2
                    ? "text"
                    : "password"
                }
                value={password2}
                onChange={(e) => {
                  setPassword2(
                    e.target.value
                  );
                  clearFieldError(
                    "password2"
                  );
                  setError("");
                }}
                placeholder="Repeat your password"
                disabled={loading}
                autoComplete="new-password"
                aria-invalid={
                  !!(
                    fieldErrors.password2 ||
                    passwordMismatch
                  )
                }
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword2(
                    (prev) => !prev
                  )
                }
                aria-label={
                  showPassword2
                    ? "Hide password"
                    : "Show password"
                }
                disabled={loading}
              >
                {showPassword2
                  ? "Hide"
                  : "Show"}
              </button>
            </div>

            {passwordMismatch && (
              <span className="field-error">
                Passwords do not match.
              </span>
            )}

            {passwordMatch && (
              <span className="field-success">
                ✓ Passwords match.
              </span>
            )}

            {fieldErrors.password2 &&
              !passwordMismatch && (
                <span className="field-error">
                  {
                    fieldErrors.password2
                  }
                </span>
              )}
          </div>

          {/* SUBMIT */}

          <button
            className="auth-button"
            type="submit"
            disabled={
              loading ||
              passwordMismatch ||
              !username.trim() ||
              !email.trim() ||
              !password ||
              !password2
            }
          >
            {loading ? (
              <>
                <span className="auth-button-spinner" />
                Creating account...
              </>
            ) : (
              <>
                Create Account
                <span className="auth-button-arrow">
                  →
                </span>
              </>
            )}
          </button>
        </form>

        {/* FOOTER */}

        <div className="auth-footer">
          <span>
            Already have an account?
          </span>

          <button
            type="button"
            onClick={() =>
              navigate("/login")
            }
            disabled={loading}
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
}

export default Register;