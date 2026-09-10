import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { requestPasswordReset } from "../services/password_reset_api";

import "./Auth.css";

function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");

  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    const trimmedEmail = email.trim().toLowerCase();

    if (!trimmedEmail) {
      setError("Please enter your email address.");
      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(trimmedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    try {
      setLoading(true);

      const data = await requestPasswordReset(
        trimmedEmail
      );

      setMessage(
        data?.detail ||
          "If an account exists with this email, a password reset link has been sent."
      );

      setEmail("");
    } catch (err) {
      setError(
        err?.message ||
          "Unable to process your password reset request."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
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
            ACCOUNT RECOVERY
          </span>

          <h2>
            Forgot your password?
          </h2>

          <p>
            Enter the email address linked to your
            account and we will send you a secure
            password reset link.
          </p>
        </div>

        {/* ===================================================
            SUCCESS MESSAGE
        =================================================== */}

        {message && (
          <div
            className="auth-alert auth-alert-success"
            role="status"
            aria-live="polite"
          >
            <span
              className="auth-alert-icon"
              aria-hidden="true"
            >
              ✓
            </span>

            <div className="auth-alert-content">
              <strong>
                Check your email
              </strong>

              <p>
                {message}
              </p>
            </div>
          </div>
        )}

        {/* ===================================================
            ERROR MESSAGE
        =================================================== */}

        {error && (
          <div
            className="auth-alert auth-alert-error"
            role="alert"
            aria-live="polite"
          >
            <span
              className="auth-alert-icon"
              aria-hidden="true"
            >
              !
            </span>

            <div className="auth-alert-content">
              <strong>
                Reset request unsuccessful
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

        {!message && (
          <form
            className="auth-form"
            onSubmit={handleSubmit}
            noValidate
          >

            <div className="auth-field">
              <div className="auth-label-row">
                <label htmlFor="forgot-password-email">
                  Email Address
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
                  id="forgot-password-email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value);
                    setError("");
                  }}
                  placeholder="Enter your email address"
                  autoComplete="email"
                  disabled={loading}
                  required
                />
              </div>
            </div>

            <button
              className="auth-button"
              type="submit"
              disabled={
                loading ||
                !email.trim()
              }
            >
              {loading ? (
                <>
                  <span
                    className="auth-button-spinner"
                    aria-hidden="true"
                  />

                  Sending reset link...
                </>
              ) : (
                <>
                  Send Reset Link

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
        )}

        {/* ===================================================
            SUCCESS ACTION
        =================================================== */}

        {message && (
          <button
            type="button"
            className="auth-button"
            onClick={() => {
              setMessage("");
              setError("");
            }}
          >
            Try Another Email
          </button>
        )}

        {/* ===================================================
            FOOTER
        =================================================== */}

        <div className="auth-footer">
          <span>
            Remember your password?
          </span>

          <Link
            to="/login"
            className="auth-footer-link"
            onClick={() => navigate("/login")}
          >
            Back to Sign In
          </Link>
        </div>

      </div>
    </main>
  );
}

export default ForgotPassword;