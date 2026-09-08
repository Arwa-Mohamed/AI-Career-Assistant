const API_URL = "http://127.0.0.1:8000";

async function parseResponse(response) {
  const contentType =
    response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    const text = await response.text();

    throw new Error(
      `Server returned non-JSON response (${response.status}): ${text.slice(
        0,
        500
      )}`
    );
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Request failed (${response.status})`
    );
  }

  return data;
}

export async function analyzeJobAgainstCV({
  cvId,
  jobDescription,
}) {
  const accessToken =
    localStorage.getItem("accessToken");

  if (!accessToken) {
    throw new Error(
      "You must be logged in before analyzing a job."
    );
  }

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

      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },

      body: JSON.stringify({
        cv_id: cvId,
        job_description:
          jobDescription.trim(),
      }),
    }
  );

  return parseResponse(response);
}