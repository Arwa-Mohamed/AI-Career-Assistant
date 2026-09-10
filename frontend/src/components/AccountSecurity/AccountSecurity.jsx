import { useEffect, useState } from "react";

import {
  getEmailStatus,
  resendEmailVerification,
  changeEmail,
  changePassword,
  deleteAccount,
} from "../../services/account_security_api";

import "./AccountSecurity.css";


function AccountSecurity() {
  // =========================================================
  // Email
  // =========================================================

  const [email, setEmail] = useState("");
  const [verified, setVerified] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);

  const [resendingVerification, setResendingVerification] =
    useState(false);


  // =========================================================
  // Change Email
  // =========================================================

  const [newEmail, setNewEmail] = useState("");
  const [changingEmail, setChangingEmail] = useState(false);


  // =========================================================
  // Change Password
  // =========================================================

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showCurrentPassword, setShowCurrentPassword] =
    useState(false);

  const [showNewPassword, setShowNewPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [changingPassword, setChangingPassword] =
    useState(false);


  // =========================================================
  // Delete Account
  // =========================================================

  const [showDeleteModal, setShowDeleteModal] =
    useState(false);

  const [deletePassword, setDeletePassword] =
    useState("");

  const [showDeletePassword, setShowDeletePassword] =
    useState(false);

  const [deletingAccount, setDeletingAccount] =
    useState(false);


  // =========================================================
  // Messages
  // =========================================================

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [deleteError, setDeleteError] = useState("");


  // =========================================================
  // Load Email Status
  // =========================================================

  useEffect(() => {
    let isMounted = true;

    const loadEmailStatus = async () => {
      try {
        setLoadingStatus(true);

        const data = await getEmailStatus();

        if (!isMounted) {
          return;
        }

        setEmail(data?.email || "");
        setVerified(Boolean(data?.verified));

      } catch (err) {
        if (!isMounted) {
          return;
        }

        setError(
          err?.message ||
            "Unable to load your email status."
        );
      } finally {
        if (isMounted) {
          setLoadingStatus(false);
        }
      }
    };

    loadEmailStatus();

    return () => {
      isMounted = false;
    };
  }, []);


  // =========================================================
  // Resend Verification
  // =========================================================

  const handleResendVerification = async () => {
    setMessage("");
    setError("");

    try {
      setResendingVerification(true);

      const data =
        await resendEmailVerification();

      setMessage(
        data?.detail ||
          "A verification email has been sent."
      );

    } catch (err) {
      setError(
        err?.message ||
          "Failed to resend verification email."
      );
    } finally {
      setResendingVerification(false);
    }
  };


  // =========================================================
  // Change Email
  // =========================================================

  const handleChangeEmail = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    const trimmedEmail =
      newEmail.trim().toLowerCase();

    if (!trimmedEmail) {
      setError(
        "Please enter your new email address."
      );
      return;
    }

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(trimmedEmail)) {
      setError(
        "Please enter a valid email address."
      );
      return;
    }

    if (
      email &&
      trimmedEmail === email.trim().toLowerCase()
    ) {
      setError(
        "This is already your current email address."
      );
      return;
    }

    try {
      setChangingEmail(true);

      const data =
        await changeEmail(trimmedEmail);

      setMessage(
        data?.detail ||
          "A verification email has been sent to your new email address."
      );

      setEmail(
        data?.email || trimmedEmail
      );

      setVerified(false);
      setNewEmail("");

    } catch (err) {
      setError(
        err?.message ||
          "Failed to change your email address."
      );
    } finally {
      setChangingEmail(false);
    }
  };


  // =========================================================
  // Change Password
  // =========================================================

  const handleChangePassword = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (
      !currentPassword ||
      !newPassword ||
      !confirmPassword
    ) {
      setError(
        "Please complete all password fields."
      );
      return;
    }

    if (newPassword.length < 8) {
      setError(
        "Your new password must contain at least 8 characters."
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(
        "New passwords do not match."
      );
      return;
    }

    try {
      setChangingPassword(true);

      const data =
        await changePassword(
          currentPassword,
          newPassword,
          confirmPassword
        );

      if (data?.access) {
        localStorage.setItem(
          "accessToken",
          data.access
        );
      }

      if (data?.refresh) {
        localStorage.setItem(
          "refreshToken",
          data.refresh
        );
      }

      setMessage(
        data?.detail ||
          "Password changed successfully."
      );

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setShowCurrentPassword(false);
      setShowNewPassword(false);
      setShowConfirmPassword(false);

    } catch (err) {
      setError(
        err?.message ||
          "Failed to change your password."
      );
    } finally {
      setChangingPassword(false);
    }
  };


  // =========================================================
  // Delete Account Modal
  // =========================================================

  const handleOpenDeleteModal = () => {
    setDeleteError("");
    setDeletePassword("");
    setShowDeletePassword(false);
    setShowDeleteModal(true);
  };


  const handleCloseDeleteModal = () => {
    if (deletingAccount) {
      return;
    }

    setShowDeleteModal(false);
    setDeleteError("");
    setDeletePassword("");
    setShowDeletePassword(false);
  };


  // =========================================================
  // Delete Account
  // =========================================================

  const handleDeleteAccount = async () => {
    setDeleteError("");

    if (!deletePassword) {
      setDeleteError(
        "Please enter your current password to confirm account deletion."
      );
      return;
    }

    try {
      setDeletingAccount(true);

      await deleteAccount(deletePassword);

      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");

      window.location.href = "/login";

    } catch (err) {
      setDeleteError(
        err?.message ||
          "Failed to delete your account."
      );

      setDeletingAccount(false);
    }
  };


  // =========================================================
  // Close Modal with Escape
  // =========================================================

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (
        event.key === "Escape" &&
        showDeleteModal &&
        !deletingAccount
      ) {
        handleCloseDeleteModal();
      }
    };

    document.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [showDeleteModal, deletingAccount]);


  // =========================================================
  // Render
  // =========================================================

  return (
    <>
      <section className="account-security-page">

        {/* =====================================================
            PAGE HEADER
        ===================================================== */}

        <div className="account-security-header">
          <div>
            <span className="account-security-eyebrow">
              ACCOUNT SECURITY
            </span>

            <h2>
              Protect your account
            </h2>

            <p>
              Manage your email, password,
              verification, and account access
              settings securely.
            </p>
          </div>
        </div>


        {/* =====================================================
            GLOBAL MESSAGES
        ===================================================== */}

        {message && (
          <div className="account-security-message success">
            <span className="account-security-message-icon">
              ✓
            </span>

            <span>
              {message}
            </span>
          </div>
        )}

        {error && (
          <div className="account-security-message error">
            <span className="account-security-message-icon">
              !
            </span>

            <span>
              {error}
            </span>
          </div>
        )}


        {/* =====================================================
            EMAIL ADDRESS
        ===================================================== */}

        <section className="account-security-card">

          <div className="account-security-card-heading">
            <div>
              <h3>
                Email Address
              </h3>

              <p>
                Your email is used for account
                verification and password recovery.
              </p>
            </div>
          </div>


          <div className="account-security-email-row">

            <div className="account-security-email-info">
              <span className="account-security-field-label">
                Current Email
              </span>

              <strong>
                {loadingStatus
                  ? "Loading..."
                  : email || "—"}
              </strong>
            </div>


            <span
              className={
                verified
                  ? "account-security-badge verified"
                  : "account-security-badge"
              }
            >
              {verified
                ? "✓ Verified"
                : "Not verified"}
            </span>

          </div>


          {!verified && !loadingStatus && (
            <div className="account-security-verification">

              <div>
                <strong>
                  Your email is not verified
                </strong>

                <p>
                  Verify your email to keep your
                  account secure and make password
                  recovery more reliable.
                </p>
              </div>

              <button
                type="button"
                className="account-security-secondary-button"
                onClick={
                  handleResendVerification
                }
                disabled={
                  resendingVerification
                }
              >
                {resendingVerification
                  ? "Sending..."
                  : "Resend Verification"}
              </button>

            </div>
          )}

        </section>


        {/* =====================================================
            CHANGE EMAIL
        ===================================================== */}

        <section className="account-security-card">

          <div className="account-security-card-heading">
            <div>
              <h3>
                Change Email Address
              </h3>

              <p>
                Enter a new email address. A
                verification email will be sent
                automatically.
              </p>
            </div>
          </div>


          <form
            className="account-security-form"
            onSubmit={handleChangeEmail}
          >

            <div className="account-security-field">

              <label htmlFor="security-new-email">
                New Email Address
              </label>

              <input
                id="security-new-email"
                type="email"
                value={newEmail}
                onChange={(event) =>
                  setNewEmail(
                    event.target.value
                  )
                }
                placeholder="you@example.com"
                autoComplete="email"
                disabled={changingEmail}
              />

              <small>
                Your new email becomes active
                after verification.
              </small>

            </div>


            <div className="account-security-form-actions">

              <button
                type="submit"
                className="account-security-primary-button"
                disabled={changingEmail}
              >
                {changingEmail
                  ? "Updating..."
                  : "Update Email"}
              </button>

            </div>

          </form>

        </section>


        {/* =====================================================
            CHANGE PASSWORD
        ===================================================== */}

        <section className="account-security-card">

          <div className="account-security-card-heading">
            <div>
              <h3>
                Change Password
              </h3>

              <p>
                Use a strong password that you
                do not reuse on other websites.
              </p>
            </div>
          </div>


          <form
            className="account-security-form"
            onSubmit={handleChangePassword}
          >

            {/* Current Password */}

            <div className="account-security-field">

              <label htmlFor="security-current-password">
                Current Password
              </label>

              <div className="account-security-password">

                <input
                  id="security-current-password"
                  type={
                    showCurrentPassword
                      ? "text"
                      : "password"
                  }
                  value={currentPassword}
                  onChange={(event) =>
                    setCurrentPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your current password"
                  autoComplete="current-password"
                  disabled={changingPassword}
                />

                <button
                  type="button"
                  className="account-security-password-toggle"
                  onClick={() =>
                    setShowCurrentPassword(
                      (previous) => !previous
                    )
                  }
                  disabled={changingPassword}
                >
                  {showCurrentPassword
                    ? "Hide"
                    : "Show"}
                </button>

              </div>

            </div>


            {/* New Password */}

            <div className="account-security-field">

              <label htmlFor="security-new-password">
                New Password
              </label>

              <div className="account-security-password">

                <input
                  id="security-new-password"
                  type={
                    showNewPassword
                      ? "text"
                      : "password"
                  }
                  value={newPassword}
                  onChange={(event) =>
                    setNewPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your new password"
                  autoComplete="new-password"
                  disabled={changingPassword}
                />

                <button
                  type="button"
                  className="account-security-password-toggle"
                  onClick={() =>
                    setShowNewPassword(
                      (previous) => !previous
                    )
                  }
                  disabled={changingPassword}
                >
                  {showNewPassword
                    ? "Hide"
                    : "Show"}
                </button>

              </div>

            </div>


            {/* Confirm Password */}

            <div className="account-security-field">

              <label htmlFor="security-confirm-password">
                Confirm New Password
              </label>

              <div className="account-security-password">

                <input
                  id="security-confirm-password"
                  type={
                    showConfirmPassword
                      ? "text"
                      : "password"
                  }
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  placeholder="Confirm your new password"
                  autoComplete="new-password"
                  disabled={changingPassword}
                />

                <button
                  type="button"
                  className="account-security-password-toggle"
                  onClick={() =>
                    setShowConfirmPassword(
                      (previous) => !previous
                    )
                  }
                  disabled={changingPassword}
                >
                  {showConfirmPassword
                    ? "Hide"
                    : "Show"}
                </button>

              </div>

              <small>
                Use at least 8 characters.
              </small>

            </div>


            <div className="account-security-form-actions">

              <button
                type="submit"
                className="account-security-primary-button"
                disabled={changingPassword}
              >
                {changingPassword
                  ? "Changing..."
                  : "Change Password"}
              </button>

            </div>

          </form>

        </section>


        {/* =====================================================
            DELETE ACCOUNT
        ===================================================== */}

        <section className="account-security-card account-security-danger-card">

          <div className="account-security-card-heading">

            <div>
              <h3>
                Delete Account
              </h3>

              <p>
                Permanently remove your account
                and associated career information.
              </p>
            </div>

          </div>


          <div className="account-security-danger-info">

            <div className="account-security-danger-mark">
              !
            </div>

            <div>
              <strong>
                This action cannot be undone.
              </strong>

              <p>
                Deleting your account will remove
                your access to your profile, CVs,
                career analysis, saved data, and
                other account-related information.
              </p>
            </div>

          </div>


          <div className="account-security-form-actions">

            <button
              type="button"
              className="account-security-danger-button"
              onClick={
                handleOpenDeleteModal
              }
            >
              Delete My Account
            </button>

          </div>

        </section>

      </section>


      {/* =======================================================
          DELETE ACCOUNT MODAL
      ======================================================= */}

      {showDeleteModal && (
        <div
          className="account-security-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
                event.currentTarget &&
              !deletingAccount
            ) {
              handleCloseDeleteModal();
            }
          }}
        >

          <div
            className="account-security-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-account-title"
          >

            <div className="account-security-modal-icon">
              !
            </div>

            <div className="account-security-modal-heading">

              <h3 id="delete-account-title">
                Delete your account?
              </h3>

              <p>
                This will permanently delete
                your account and its associated
                data. This action cannot be
                undone.
              </p>

            </div>


            <div className="account-security-modal-warning">

              <strong>
                Please confirm your identity
              </strong>

              <span>
                Enter your current password to
                continue with account deletion.
              </span>

            </div>


            <div className="account-security-field">

              <label htmlFor="delete-account-password">
                Current Password
              </label>

              <div className="account-security-password">

                <input
                  id="delete-account-password"
                  type={
                    showDeletePassword
                      ? "text"
                      : "password"
                  }
                  value={deletePassword}
                  onChange={(event) =>
                    setDeletePassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your current password"
                  autoComplete="current-password"
                  disabled={deletingAccount}
                />

                <button
                  type="button"
                  className="account-security-password-toggle"
                  onClick={() =>
                    setShowDeletePassword(
                      (previous) => !previous
                    )
                  }
                  disabled={deletingAccount}
                >
                  {showDeletePassword
                    ? "Hide"
                    : "Show"}
                </button>

              </div>

            </div>


            {deleteError && (
              <div className="account-security-message error modal-error">

                <span className="account-security-message-icon">
                  !
                </span>

                <span>
                  {deleteError}
                </span>

              </div>
            )}


            <div className="account-security-modal-actions">

              <button
                type="button"
                className="account-security-secondary-button"
                onClick={
                  handleCloseDeleteModal
                }
                disabled={deletingAccount}
              >
                Cancel
              </button>

              <button
                type="button"
                className="account-security-danger-button"
                onClick={
                  handleDeleteAccount
                }
                disabled={deletingAccount}
              >
                {deletingAccount
                  ? "Deleting..."
                  : "Delete Account"}
              </button>

            </div>

          </div>

        </div>
      )}
    </>
  );
}


export default AccountSecurity;