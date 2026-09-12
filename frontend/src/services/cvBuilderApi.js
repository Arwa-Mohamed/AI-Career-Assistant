const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function getAuthHeaders(includeJson = true) {
  const token = localStorage.getItem("accessToken");

  return {
    ...(includeJson
      ? {
          "Content-Type": "application/json",
        }
      : {}),
    ...(token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {}),
  };
}

async function parseResponse(response) {
  const contentType =
    response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return null;
}

/**
 * Generate and download the final CV PDF.
 *
 * The endpoint remains:
 * POST /api/cvs/generate-pdf/
 *
 * The backend supports both:
 * - the old payload
 * - the new structured CV Builder payload
 */
export async function generateCVPDF(payload = {}) {
  const response = await fetch(
    `${API_URL}/api/cvs/generate-pdf/`,
    {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    let errorMessage =
      "Failed to generate CV PDF.";

    try {
      const data = await parseResponse(response);

      errorMessage =
        data?.detail ||
        data?.message ||
        data?.error ||
        errorMessage;
    } catch {
      // Keep default message.
    }

    throw new Error(errorMessage);
  }

  const blob = await response.blob();

  const url =
    window.URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;

  link.download =
    "AI_Career_Assistant_CV.pdf";

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}

/**
 * Analyze the source CV using the existing CV Analysis pipeline.
 *
 * Existing endpoint:
 * POST /api/cv-analysis/<cv_id>/
 */
export async function analyzeCVBuilder(cvId) {
  if (!cvId) {
    throw new Error(
      "Please select a CV first."
    );
  }

  const response = await fetch(
    `${API_URL}/api/cv-analysis/${cvId}/`,
    {
      method: "POST",
      headers: getAuthHeaders(false),
    }
  );

  const contentType =
    response.headers.get("content-type") || "";

  let data = {};

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const text = await response.text();

    throw new Error(
      `Server returned non-JSON response (${response.status}): ${text.slice(
        0,
        250
      )}`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        data?.error ||
        "Failed to analyze CV."
    );
  }

  return data;
}

/**
 * Analyze a CV against a specific job description
 * using the existing taxonomy-driven Job Intelligence endpoint.
 *
 * Existing endpoint:
 * POST /api/career-taxonomy/job-match/
 */
export async function analyzeCVAgainstJob(
  cvId,
  jobDescription
) {
  if (!cvId) {
    throw new Error(
      "Please select a CV first."
    );
  }

  if (
    !jobDescription ||
    jobDescription.trim().length < 30
  ) {
    throw new Error(
      "Please enter a complete job description."
    );
  }

  const response = await fetch(
    `${API_URL}/api/career-taxonomy/job-match/`,
    {
      method: "POST",
      headers: getAuthHeaders(true),
      body: JSON.stringify({
        cv_id: cvId,
        job_description:
          jobDescription.trim(),
      }),
    }
  );

  const contentType =
    response.headers.get("content-type") || "";

  let data = {};

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const text = await response.text();

    throw new Error(
      `Server returned non-JSON response (${response.status}): ${text.slice(
        0,
        250
      )}`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        data?.error ||
        "Failed to analyze the CV against this job."
    );
  }

  return data;
}