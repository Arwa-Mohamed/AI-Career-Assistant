const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

/**
 * Request a password reset email.
 */
export async function requestPasswordReset(email) {
  const response = await fetch(
    `${API_URL}/api/auth/password/reset/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
      }),
    }
  );

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const detail = data?.detail;

    if (Array.isArray(detail)) {
      throw new Error(detail.join(" "));
    }

    throw new Error(
      detail ||
        "Unable to send the password reset email."
    );
  }

  return data;
}

/**
 * Confirm password reset using the uid and token
 * received in the reset email.
 */
export async function confirmPasswordReset({
  uid,
  token,
  newPassword,
  confirmPassword,
}) {
  const response = await fetch(
    `${API_URL}/api/auth/password/reset/confirm/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        uid,
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    }
  );

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const detail = data?.detail;

    if (Array.isArray(detail)) {
      throw new Error(detail.join(" "));
    }

    throw new Error(
      detail ||
        "Unable to reset your password."
    );
  }

  return data;
}