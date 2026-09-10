import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { confirmPasswordReset } from "../services/password_reset_api";

import "./ResetPassword.css";

function ResetPassword() {
  const navigate = useNavigate();
  const { uid, token } = useParams();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);

  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [fieldErrors, setFieldErrors] = useState({});

  const passwordRequirements = {
    minLength: newPassword.length >= 8,
    matched:
      newPassword.length > 0 &&
      confirmPassword.length > 0 &&
      newPassword === confirmPassword,
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

    setError("");
  };

  const validateForm = () => {
    const errors = {};

    if (!newPassword) {
      errors.newPassword =
        "Please enter your new password.";
    } else if (newPassword.length < 8) {
      errors.newPassword =
        "Password must contain at least 8 characters.";
    }

    if (!confirmPassword) {
      errors.confirmPassword =
        "Please confirm your new password.";
    } else if (newPassword !== confirmPassword) {
      errors.confirmPassword =
        "Passwords do not match.";
    }

    if (!uid || !token) {
      setError(
        "This password reset link is invalid or incomplete."
      );
      return false;
    }

    setFieldErrors(errors);

    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");
    setSuccess(false);

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      const data = await confirmPasswordReset({
        uid,
        token,
        newPassword,
        confirmPassword,
      });

      setSuccess(true);

      setMessage(
        data?.detail ||
          "Your password has been reset successfully."
      );

      setNewPassword("");
      setConfirmPassword("");
      setFieldErrors({});

      window.setTimeout(() => {
        navigate("/login");
      }, 4000);
    } catch (err) {
      setError(
        err?.message ||
          "Unable to reset your password. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="reset-password-page">
      <div className="reset-password-shell">
        <section className="reset-password-card">

          {/* =================================================
              BRAND
          ================================================= */}

          <div className="reset-password-brand">
            <div className="reset-password-logo">
              AI
            </div>

            <div className="reset-password-brand-text">
              <h1>Career Assistant</h1>

              <p>
                AI-powered career guidance
              </p>
            </div>
          </div>

          {/* =================================================
              SUCCESS STATE
          ================================================= */}

          {success ? (
            <div className="reset-password-success-state">
              <div className="reset-password-success-icon">
                ✓
              </div>

              <h2>
                Password reset successful
              </h2>

              <p>
                {message}
              </p>

              <Link
                to="/login"
                className="reset-password-login-button"
              >
                Continue to Sign In
              </Link>
            </div>
          ) : (
            <>
              {/* =============================================
                  HEADER
              ============================================= */}

              <div className="reset-password-header">
                <span className="reset-password-kicker">
                  ACCOUNT SECURITY
                </span>

                <h2>
                  Create a new password
                </h2>

                <p>
                  Choose a strong password to secure
                  your AI Career Assistant account.
                </p>
              </div>

              {/* =============================================
                  ERROR
              ============================================= */}

              {error && (
                <div
                  className="reset-password-alert error"
                  role="alert"
                  aria-live="polite"
                >
                  <span className="reset-password-alert-icon">
                    !
                  </span>

                  <div className="reset-password-alert-content">
                    <strong>
                      Password reset unsuccessful
                    </strong>

                    <p>
                      {error}
                    </p>
                  </div>
                </div>
              )}

              {/* =============================================
                  FORM
              ============================================= */}

              <form
                className="reset-password-form"
                onSubmit={handleSubmit}
                noValidate
              >

                {/* NEW PASSWORD */}

                <div
                  className={`reset-password-field ${
                    fieldErrors.newPassword
                      ? "has-error"
                      : ""
                  }`}
                >
                  <div className="reset-password-label-row">
                    <label htmlFor="reset-new-password">
                      New Password
                    </label>
                  </div>

                  <div className="reset-password-input-wrap">
                    <input
                      id="reset-new-password"
                      name="new_password"
                      className="reset-password-input"
                      type={
                        showNewPassword
                          ? "text"
                          : "password"
                      }
                      value={newPassword}
                      onChange={(event) => {
                        setNewPassword(
                          event.target.value
                        );

                        clearFieldError(
                          "newPassword"
                        );
                      }}
                      placeholder="Enter your new password"
                      autoComplete="new-password"
                      disabled={loading}
                      required
                    />

                    <button
                      type="button"
                      className="reset-password-toggle"
                      onClick={() =>
                        setShowNewPassword(
                          (previous) => !previous
                        )
                      }
                      disabled={loading}
                    >
                      {showNewPassword
                        ? "Hide"
                        : "Show"}
                    </button>
                  </div>

                  {fieldErrors.newPassword && (
                    <p className="reset-password-field-error">
                      {fieldErrors.newPassword}
                    </p>
                  )}
                </div>

                {/* CONFIRM PASSWORD */}

                <div
                  className={`reset-password-field ${
                    fieldErrors.confirmPassword
                      ? "has-error"
                      : ""
                  }`}
                >
                  <div className="reset-password-label-row">
                    <label htmlFor="reset-confirm-password">
                      Confirm New Password
                    </label>
                  </div>

                  <div className="reset-password-input-wrap">
                    <input
                      id="reset-confirm-password"
                      name="confirm_password"
                      className="reset-password-input"
                      type={
                        showConfirmPassword
                          ? "text"
                          : "password"
                      }
                      value={confirmPassword}
                      onChange={(event) => {
                        setConfirmPassword(
                          event.target.value
                        );

                        clearFieldError(
                          "confirmPassword"
                        );
                      }}
                      placeholder="Confirm your new password"
                      autoComplete="new-password"
                      disabled={loading}
                      required
                    />

                    <button
                      type="button"
                      className="reset-password-toggle"
                      onClick={() =>
                        setShowConfirmPassword(
                          (previous) => !previous
                        )
                      }
                      disabled={loading}
                    >
                      {showConfirmPassword
                        ? "Hide"
                        : "Show"}
                    </button>
                  </div>

                  {fieldErrors.confirmPassword && (
                    <p className="reset-password-field-error">
                      {fieldErrors.confirmPassword}
                    </p>
                  )}
                </div>

                {/* REQUIREMENTS */}

                <div className="reset-password-requirements">
                  <div
                    className={`reset-password-requirement ${
                      passwordRequirements.minLength
                        ? "valid"
                        : ""
                    }`}
                  >
                    <span className="reset-password-requirement-icon">
                      {passwordRequirements.minLength
                        ? "✓"
                        : "•"}
                    </span>

                    <span>
                      At least 8 characters
                    </span>
                  </div>

                  <div
                    className={`reset-password-requirement ${
                      passwordRequirements.matched
                        ? "valid"
                        : ""
                    }`}
                  >
                    <span className="reset-password-requirement-icon">
                      {passwordRequirements.matched
                        ? "✓"
                        : "•"}
                    </span>

                    <span>
                      Passwords match
                    </span>
                  </div>
                </div>

                {/* SUBMIT */}

                <button
                  type="submit"
                  className="reset-password-submit"
                  disabled={
                    loading ||
                    !newPassword ||
                    !confirmPassword
                  }
                >
                  {loading
                    ? "Resetting password..."
                    : "Reset Password"}
                </button>
              </form>

              {/* =============================================
                  FOOTER
              ============================================= */}

              <div className="reset-password-footer">
                <span>
                  Remember your password?
                </span>

                <Link to="/login">
                  Back to Sign In
                </Link>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default ResetPassword;