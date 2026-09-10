import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import "./EmailVerified.css";

function EmailVerified() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/login");
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <main className="email-verified-page">
      <div className="email-verified-background">
        <div className="email-verified-card">
          <div className="email-verified-icon">
            <span>✓</span>
          </div>

          <div className="email-verified-badge">
            EMAIL VERIFIED
          </div>

          <h1>Your email is verified!</h1>

          <p className="email-verified-description">
            Your email address has been successfully verified.
            Your AI Career Assistant account is now ready to use.
          </p>

          <div className="email-verified-status">
            <div className="email-verified-status-icon">
              ✓
            </div>

            <div>
              <strong>Account verification complete</strong>
              <span>
                You can now sign in and continue building your career journey.
              </span>
            </div>
          </div>

          <Link
            to="/login"
            className="email-verified-primary-button"
          >
            Continue to Login
          </Link>

          <p className="email-verified-redirect">
            Redirecting you to login in a few seconds...
          </p>
        </div>
      </div>
    </main>
  );
}

export default EmailVerified;