const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


// =========================================================
// Authenticated Request
// =========================================================

async function authenticatedFetch(
  path,
  options = {}
) {
  const accessToken =
    localStorage.getItem("accessToken");

  const headers = {
    ...(options.headers || {}),
  };

  if (accessToken) {
    headers.Authorization =
      `Bearer ${accessToken}`;
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers["Content-Type"]
  ) {
    headers["Content-Type"] =
      "application/json";
  }

  const response = await fetch(
    `${API_URL}${path}`,
    {
      ...options,
      headers,
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
      throw new Error(
        detail.join(" ")
      );
    }

    throw new Error(
      detail ||
        data?.error ||
        "Request failed."
    );
  }

  return data;
}


// =========================================================
// Email Status
// =========================================================

export async function getEmailStatus() {
  return authenticatedFetch(
    "/api/auth/email/status/",
    {
      method: "GET",
    }
  );
}


// =========================================================
// Resend Email Verification
// =========================================================

export async function resendEmailVerification() {
  return authenticatedFetch(
    "/api/auth/email/resend/",
    {
      method: "POST",
      body: JSON.stringify({}),
    }
  );
}


// =========================================================
// Change Email
// =========================================================

export async function changeEmail(
  newEmail
) {
  return authenticatedFetch(
    "/api/auth/email/change/",
    {
      method: "POST",
      body: JSON.stringify({
        new_email: newEmail,
      }),
    }
  );
}


// =========================================================
// Change Password
// =========================================================

export async function changePassword(
  currentPassword,
  newPassword,
  confirmPassword
) {
  return authenticatedFetch(
    "/api/auth/password/change/",
    {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    }
  );
}


// =========================================================
// Delete Account
// =========================================================

export async function deleteAccount(
  currentPassword
) {
  return authenticatedFetch(
    "/api/auth/account/delete/",
    {
      method: "DELETE",
      body: JSON.stringify({
        current_password: currentPassword,
      }),
    }
  );
}