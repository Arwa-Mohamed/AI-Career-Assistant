const API_URL = "http://127.0.0.1:8000";


// =========================
// Token Refresh
// =========================

async function refreshAccessToken() {
  const refreshToken =
    localStorage.getItem("refreshToken");

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${API_URL}/api/auth/refresh/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      }
    );

    if (!response.ok) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");

      return null;
    }

    const data =
      await response.json();

    if (!data.access) {
      return null;
    }

    localStorage.setItem(
      "accessToken",
      data.access
    );

    return data.access;
  } catch {
    return null;
  }
}


// =========================
// Main API Fetch
// =========================

async function apiFetch(
  url,
  options = {},
  retry = true
) {
  const token =
    localStorage.getItem("accessToken");

  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }

  const response = await fetch(
    url,
    {
      ...options,
      headers,
    }
  );

  if (
    response.status !== 401 ||
    !retry
  ) {
    return response;
  }

  const newToken =
    await refreshAccessToken();

  if (!newToken) {
    return response;
  }

  return apiFetch(
    url,
    {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization:
          `Bearer ${newToken}`,
      },
    },
    false
  );
}


// =========================
// Health
// =========================

export async function healthCheck() {
  const response = await fetch(
    `${API_URL}/api/health/`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to connect to backend"
    );
  }

  return response.json();
}


// =========================
// Authentication
// =========================

export async function loginUser(
  username,
  password
) {
  const response = await fetch(
    `${API_URL}/api/auth/login/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        username,
        password,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Login failed"
    );
  }

  return data;
}


export async function registerUser(
  username,
  email,
  password,
  password2
) {
  const response = await fetch(
    `${API_URL}/api/auth/register/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        username,
        email,
        password,
        password2,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    const firstError =
      Object.values(data)?.[0];

    throw new Error(
      Array.isArray(firstError)
        ? firstError[0]
        : data.detail ||
          data.message ||
          "Registration failed."
    );
  }

  return data;
}


// =========================
// Profile
// =========================

export async function getProfile() {
  const response = await apiFetch(
    `${API_URL}/api/profile/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load profile"
    );
  }

  return data;
}


export async function updateProfile(
  profileData
) {
  const response = await apiFetch(
    `${API_URL}/api/profile/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        profileData
      ),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to update profile"
    );
  }

  return data;
}


// =========================
// Dashboard
// =========================

export async function getDashboard() {
  const response = await apiFetch(
    `${API_URL}/api/dashboard/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load dashboard"
    );
  }

  return data;
}


// =========================
// CV
// =========================

export async function getCVs() {
  const response = await apiFetch(
    `${API_URL}/api/cvs/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "Failed to load CVs"
    );
  }

  if (Array.isArray(data)) {
    return data;
  }

  if (
    data &&
    Array.isArray(data.results)
  ) {
    return data.results;
  }

  return [];
}


export async function getMyCVs() {
  return getCVs();
}


export async function uploadCV(
  title,
  file
) {
  const formData =
    new FormData();

  formData.append(
    "title",
    title
  );

  formData.append(
    "file",
    file
  );

  const response = await apiFetch(
    `${API_URL}/api/cvs/`,
    {
      method: "POST",
      body: formData,
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    const firstError =
      Object.values(data)?.[0];

    throw new Error(
      Array.isArray(firstError)
        ? firstError[0]
        : data.detail ||
          "Failed to upload CV"
    );
  }

  return data;
}


export async function deleteCV(
  cvId
) {
  const response = await apiFetch(
    `${API_URL}/api/cvs/${cvId}/`,
    {
      method: "DELETE",
    }
  );

  if (
    !response.ok &&
    response.status !== 204
  ) {
    let data = {};

    try {
      data =
        await response.json();
    } catch {
      // No JSON body
    }

    throw new Error(
      data.detail ||
      "Failed to delete CV"
    );
  }
}


// =========================
// CV Analysis
// =========================

export async function analyzeCV(
  cvId
) {
  const response = await apiFetch(
    `${API_URL}/api/cv-analysis/${cvId}/`,
    {
      method: "POST",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.error ||
      "Failed to analyze CV"
    );
  }

  return data;
}


// =========================
// Job Matching - Existing
// =========================

export async function matchJob(
  cvId,
  jobDescription
) {
  const response = await apiFetch(
    `${API_URL}/api/job-matching/${cvId}/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        job_description:
          jobDescription,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to analyze job"
    );
  }

  return data;
}


export async function getJobHistory() {
  const response = await apiFetch(
    `${API_URL}/api/job-matching/history/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load job history"
    );
  }

  return data;
}


// =========================
// Job Intelligence - Career Taxonomy
// =========================

export async function analyzeCareerJobMatch(
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

  const response = await apiFetch(
    `${API_URL}/api/career-taxonomy/job-match/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        cv_id: cvId,
        job_description:
          jobDescription.trim(),
      }),
    }
  );

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  let data = {};

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    data =
      await response.json();
  } else {
    const text =
      await response.text();

    throw new Error(
      `Server returned non-JSON response (${response.status}): ${text.slice(
        0,
        300
      )}`
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.error ||
      "Failed to analyze job with Career Intelligence."
    );
  }

  return data;
}


// =========================
// Skill Gap
// =========================

export async function createSkillGap(
  jobAnalysisId
) {
  const response = await apiFetch(
    `${API_URL}/api/skill-gap/${jobAnalysisId}/`,
    {
      method: "POST",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to analyze skill gap"
    );
  }

  return data;
}


// =========================
// Chatbot
// =========================

export async function sendChatMessage(
  message,
  sessionId = null
) {
  const response = await apiFetch(
    `${API_URL}/api/chatbot/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        message,
        session_id:
          sessionId,
      }),
    }
  );

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  if (
    !contentType.includes(
      "application/json"
    )
  ) {
    const text =
      await response.text();

    throw new Error(
      `Server returned non-JSON response (${response.status}): ${text.slice(
        0,
        200
      )}`
    );
  }

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.error ||
      "Failed to send message"
    );
  }

  return data;
}


// =========================
// Interviews
// =========================

export async function startInterview(
  cvId,
  jobAnalysisId,
  role
) {
  const response = await apiFetch(
    `${API_URL}/api/interviews/start/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        cv_id: cvId,
        job_analysis_id:
          jobAnalysisId || null,
        role,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to start interview"
    );
  }

  return data;
}


export async function submitInterviewAnswer(
  questionId,
  answer
) {
  const response = await apiFetch(
    `${API_URL}/api/interviews/questions/${questionId}/answer/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        answer,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to evaluate answer"
    );
  }

  return data;
}


export async function completeInterview(
  sessionId
) {
  const response = await apiFetch(
    `${API_URL}/api/interviews/${sessionId}/complete/`,
    {
      method: "POST",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to complete interview"
    );
  }

  return data;
}


export async function getInterviewHistory() {
  const response = await apiFetch(
    `${API_URL}/api/interviews/history/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load interview history"
    );
  }

  return data;
}


// =========================
// Social Login
// =========================

export async function exchangeSocialLoginCode(
  code
) {
  const response = await fetch(
    `${API_URL}/api/auth/social/exchange/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        code,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.error ||
      "Social login failed."
    );
  }

  return data;
}


// =========================
// Career Projects
// =========================

export async function getCareerProjects() {
  const response = await apiFetch(
    `${API_URL}/api/projects/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to load projects."
    );
  }

  return data;
}


export async function createCareerProject(
  projectData
) {
  const response = await apiFetch(
    `${API_URL}/api/projects/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        projectData
      ),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to create project."
    );
  }

  return data;
}


export async function updateCareerProject(
  projectId,
  updateData
) {
  const response = await apiFetch(
    `${API_URL}/api/projects/${projectId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        updateData
      ),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to update project."
    );
  }

  return data;
}


export async function deleteCareerProject(
  projectId
) {
  const response = await apiFetch(
    `${API_URL}/api/projects/${projectId}/`,
    {
      method: "DELETE",
    }
  );

  if (
    !response.ok &&
    response.status !== 204
  ) {
    let data = {};

    try {
      data =
        await response.json();
    } catch {
      // No JSON body
    }

    throw new Error(
      data.detail ||
      "Failed to delete project."
    );
  }
}


export async function getProjectRecommendations() {
  const response = await apiFetch(
    `${API_URL}/api/projects/recommendations/`,
    {
      method: "GET",
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to generate project recommendations."
    );
  }

  return data;
}


export async function addProjectToCV(
  cvId,
  projectId
) {
  const response = await apiFetch(
    `${API_URL}/api/cvs/${cvId}/projects/${projectId}/`,
    {
      method: "POST",
    }
  );

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  let data;

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    data =
      await response.json();
  } else {
    throw new Error(
      `Backend returned a non-JSON response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to add project to CV."
    );
  }

  return data;
}


export async function removeProjectFromCV(
  cvId,
  projectId
) {
  const response = await apiFetch(
    `${API_URL}/api/cvs/${cvId}/projects/${projectId}/remove/`,
    {
      method: "DELETE",
    }
  );

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  let data;

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    data =
      await response.json();
  } else {
    throw new Error(
      `Backend returned a non-JSON response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to remove project from CV."
    );
  }

  return data;
}

// =========================
// Profile Image
// =========================

export async function updateProfileImage(imageFile) {
  if (!imageFile) {
    throw new Error("Please select an image first.");
  }

  const formData = new FormData();
  formData.append("profile_image", imageFile);

  const response = await apiFetch(
    `${API_URL}/api/profile/`,
    {
      method: "PATCH",
      body: formData,
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
        300
      )}`
    );
  }

  if (!response.ok) {
    const firstError = Object.values(data)?.[0];

    throw new Error(
      Array.isArray(firstError)
        ? firstError[0]
        : data.detail ||
          data.error ||
          "Failed to upload profile image."
    );
  }

  return data;
}