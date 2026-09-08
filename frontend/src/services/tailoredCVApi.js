const API_URL = "http://127.0.0.1:8000";

export async function tailorCV({
  jobTitle,
  jobDescription,
  requiredSkills = [],
  cvId = null,
}) {
  const token =
    localStorage.getItem("accessToken");

  const response = await fetch(
    `${API_URL}/api/cvs/tailor/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
      },

      body: JSON.stringify({
        job_title: jobTitle,
        job_description: jobDescription,
        required_skills: requiredSkills,
        cv_id: cvId,
      }),
    }
  );

  let data = null;

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    data = await response.json();
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        "Failed to tailor your CV."
    );
  }

  return data;
}


export async function generateTailoredCVPDF({
  jobTitle,
  tailoredSummary,
  matchedSkills = [],
  recommendedProjectIds = [],
  cvId = null,
}) {
  const token =
    localStorage.getItem("accessToken");

  const response = await fetch(
    `${API_URL}/api/cvs/tailor/generate-pdf/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
      },

      body: JSON.stringify({
        job_title: jobTitle,

        tailored_summary:
          tailoredSummary,

        matched_skills:
          matchedSkills,

        recommended_project_ids:
          recommendedProjectIds,

        cv_id: cvId,
      }),
    }
  );

  if (!response.ok) {
    let message =
      "Failed to generate tailored CV.";

    try {
      const data =
        await response.json();

      message =
        data?.detail ||
        data?.message ||
        message;
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  const blob =
    await response.blob();

  const url =
    window.URL.createObjectURL(
      blob
    );

  const link =
    document.createElement("a");

  link.href = url;
  link.download =
    "Tailored_CV.pdf";

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}