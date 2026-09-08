import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getDashboard,
  getInterviewHistory,
  getCareerProjects,
  getProfile,
} from "../services/api";

import "./Dashboard.css";

const API_URL = "http://127.0.0.1:8000";

function getMediaUrl(value) {
  if (!value) {
    return "";
  }

  if (
    value.startsWith("http://") ||
    value.startsWith("https://") ||
    value.startsWith("blob:") ||
    value.startsWith("data:")
  ) {
    return value;
  }

  if (value.startsWith("/")) {
    return `${API_URL}${value}`;
  }

  return `${API_URL}/${value}`;
}

function Dashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [projects, setProjects] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =========================================================
  // LOAD DASHBOARD DATA
  // =========================================================

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        setError("");

        const [
          dashboardData,
          interviewData,
          projectData,
          profileData,
        ] = await Promise.all([
          getDashboard(),
          getInterviewHistory(),
          getCareerProjects(),
          getProfile(),
        ]);

        if (!mounted) {
          return;
        }

        setDashboard({
          ...(dashboardData || {}),
          profile: {
            ...(dashboardData?.profile || {}),
            ...(profileData || {}),
          },
        });

        setInterviews(
          Array.isArray(interviewData)
            ? interviewData
            : []
        );

        setProjects(
          Array.isArray(projectData)
            ? projectData
            : []
        );
      } catch (err) {
        if (!mounted) {
          return;
        }

        setError(
          err?.message ||
            "Failed to load your career dashboard."
        );
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      mounted = false;
    };
  }, []);

  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <div className="dashboard-loading-spinner" />

          <div className="dashboard-loading-copy">
            <span className="dashboard-loading-eyebrow">
              AI CAREER INTELLIGENCE
            </span>

            <strong>
              Loading your career dashboard
            </strong>

            <span>
              Bringing together your CV, skills,
              projects and interview progress.
            </span>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================
  // ERROR STATE
  // =========================================================

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">

          <div className="dashboard-error-icon">
            !
          </div>

          <div className="dashboard-error-content">
            <span className="dashboard-section-eyebrow">
              DASHBOARD ERROR
            </span>

            <h2>
              We couldn't load your dashboard
            </h2>

            <p>
              {error}
            </p>
          </div>

          <button
            type="button"
            className="dashboard-primary-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Try Again
          </button>

        </div>
      </div>
    );
  }

  // =========================================================
  // BASIC DATA
  // =========================================================

  const userName =
    dashboard?.user?.username ||
    dashboard?.user?.name ||
    dashboard?.user?.full_name ||
    "Career Explorer";

  const profile =
    dashboard?.profile || {};

  const profileName =
    profile.full_name ||
    userName;

  const profileImage = getMediaUrl(
    profile?.profile_image || ""
  );

  const careerGoal =
    profile.career_goal ||
    "Add your career goal";

  const profileLocation =
    profile.location || "";

  const avatarLetter =
    profileName
      ?.trim()
      ?.charAt(0)
      ?.toUpperCase() || "A";

  const skills =
    Array.isArray(
      dashboard?.cv?.parsed_data?.skills
    )
      ? dashboard.cv.parsed_data.skills
      : [];

  const missingSkills =
    Array.isArray(
      dashboard?.skill_gap?.missing_skills
    )
      ? dashboard.skill_gap.missing_skills
      : [];

  const matchedSkills =
    Array.isArray(
      dashboard?.skill_gap?.matched_skills
    )
      ? dashboard.skill_gap.matched_skills
      : [];

  const requiredSkills =
    Array.isArray(
      dashboard?.skill_gap?.required_skills
    )
      ? dashboard.skill_gap.required_skills
      : [];

  const roadmap =
    Array.isArray(
      dashboard?.skill_gap?.learning_roadmap
    )
      ? dashboard.skill_gap.learning_roadmap
      : [];

  const jobHistory =
    Array.isArray(
      dashboard?.job_history
    )
      ? dashboard.job_history
      : [];

  // =========================================================
  // MAIN SCORES
  // =========================================================

  const cvScore = Math.min(
    Math.max(
      Number(dashboard?.cv_score) || 0,
      0
    ),
    100
  );

  const jobMatch = Math.min(
    Math.max(
      Number(
        dashboard?.latest_job_match
      ) || 0,
      0
    ),
    100
  );

  // =========================================================
  // SORT INTERVIEWS BY MOST RECENT
  // =========================================================

  const sortedInterviews = [...interviews].sort(
    (a, b) => {
      const dateA = new Date(
        a?.created_at ||
          a?.createdAt ||
          a?.date ||
          0
      );

      const dateB = new Date(
        b?.created_at ||
          b?.createdAt ||
          b?.date ||
          0
      );

      return dateB - dateA;
    }
  );

  const latestInterview =
    sortedInterviews.length > 0
      ? sortedInterviews[0]
      : null;

  const latestInterviewScore =
    Math.min(
      Math.max(
        Number(
          latestInterview?.score
        ) || 0,
        0
      ),
      100
    );

  // =========================================================
  // PROFILE COMPLETENESS
  // =========================================================

  const profileFields = [
    profile.full_name,
    profile.phone,
    profile.location,
    profile.bio,
    profile.career_goal,
    profile.linkedin_url,
  ];

  const completedProfileFields =
    profileFields.filter(
      (field) =>
        field &&
        String(field).trim() !== ""
    ).length;

  const profileCompleteness =
    profileFields.length > 0
      ? Math.round(
          (completedProfileFields /
            profileFields.length) *
            100
        )
      : 0;

  // =========================================================
  // SKILL ALIGNMENT
  // =========================================================

  const skillAlignment =
    requiredSkills.length > 0
      ? Math.min(
          Math.round(
            (matchedSkills.length /
              requiredSkills.length) *
              100
          ),
          100
        )
      : Math.min(
          skills.length * 5,
          100
        );

  // =========================================================
  // CAREER READINESS
  // =========================================================

  const careerReadinessScore =
    Math.round(
      cvScore * 0.25 +
        skillAlignment * 0.25 +
        jobMatch * 0.20 +
        latestInterviewScore * 0.20 +
        profileCompleteness * 0.10
    );

  const readinessScore =
    Math.min(
      Math.max(
        careerReadinessScore,
        0
      ),
      100
    );

  // =========================================================
  // READINESS STATUS
  // =========================================================

  let readinessLabel =
    "Getting Started";

  let readinessDescription =
    "You are building your career foundation.";

  let readinessTone =
    "starter";

  if (readinessScore >= 85) {
    readinessLabel =
      "Highly Ready";

    readinessDescription =
      "You are strongly prepared for your target opportunities.";

    readinessTone =
      "excellent";
  } else if (readinessScore >= 70) {
    readinessLabel =
      "Career Ready";

    readinessDescription =
      "You have a strong foundation with a few areas to improve.";

    readinessTone =
      "strong";
  } else if (readinessScore >= 50) {
    readinessLabel =
      "Almost Ready";

    readinessDescription =
      "You are making good progress. Focus on your main skill gaps.";

    readinessTone =
      "developing";
  } else if (readinessScore >= 30) {
    readinessLabel =
      "Building";

    readinessDescription =
      "You have started your journey. More profile, CV and skill work is needed.";

    readinessTone =
      "building";
  }

  // =========================================================
  // READINESS BREAKDOWN
  // =========================================================

  const readinessBreakdown = [
    {
      label: "CV Quality",
      shortLabel: "CV",
      value: cvScore,
      weight: "25%",
    },
    {
      label: "Skill Alignment",
      shortLabel: "Skills",
      value: skillAlignment,
      weight: "25%",
    },
    {
      label: "Job Match",
      shortLabel: "Jobs",
      value: jobMatch,
      weight: "20%",
    },
    {
      label: "Interview",
      shortLabel: "Interview",
      value: latestInterviewScore,
      weight: "20%",
    },
    {
      label: "Profile",
      shortLabel: "Profile",
      value: profileCompleteness,
      weight: "10%",
    },
  ];

  // =========================================================
  // DERIVED CAREER INSIGHTS
  // =========================================================

  const strongestSignal =
    [...readinessBreakdown].sort(
      (a, b) => b.value - a.value
    )[0];

  const biggestOpportunity =
    [...readinessBreakdown].sort(
      (a, b) => a.value - b.value
    )[0];

  const skillGapCount =
    missingSkills.length;

  const detectedSkillCount =
    skills.length;

  const matchedSkillCount =
    matchedSkills.length;

  const requiredSkillCount =
    requiredSkills.length;

  const careerFocus =
    biggestOpportunity?.label ||
    "Career Profile";

  const careerFocusValue =
    Math.round(
      biggestOpportunity?.value || 0
    );

  const readinessMomentum =
    readinessScore >= 85
      ? "You're in a strong position."
      : readinessScore >= 70
      ? "You're close to a highly competitive profile."
      : readinessScore >= 50
      ? "A few focused improvements can move you forward."
      : "Start with the highest-impact foundations.";

  // =========================================================
  // SNAPSHOT STATS
  // =========================================================

  const dashboardStats = [
    {
      label: "Skills detected",
      value: detectedSkillCount,
      detail: "From your current CV",
      tone: "neutral",
    },
    {
      label: "Skills matched",
      value: matchedSkillCount,
      detail:
        requiredSkillCount > 0
          ? `of ${requiredSkillCount} required`
          : "Against target roles",
      tone: "success",
    },
    {
      label: "Skill gaps",
      value: skillGapCount,
      detail:
        skillGapCount > 0
          ? "Worth focusing on"
          : "No major gaps detected",
      tone:
        skillGapCount > 0
          ? "warning"
          : "success",
    },
    {
      label: "Projects",
      value: projects.length,
      detail:
        projects.length > 0
          ? "Career project portfolio"
          : "Start building evidence",
      tone: "primary",
    },
  ];

  // =========================================================
  // NEXT BEST ACTIONS
  // =========================================================

  const nextActions = [];

  if (cvScore < 70) {
    nextActions.push({
      title: "Improve your CV",
      description:
        "Your CV score is below 70. Improve its structure, content, and relevance.",
      action: "View CV",
      path: "/cv",
      priority: "High",
    });
  }

  if (skillAlignment < 70) {
    nextActions.push({
      title: "Close your skill gaps",
      description:
        "You are missing important skills required for your target role.",
      action: "Analyze Skills",
      path: "/jobs",
      priority: "High",
    });
  }

  if (jobMatch < 70) {
    nextActions.push({
      title: "Improve job alignment",
      description:
        "Your current CV does not strongly match your latest target job.",
      action: "Review Job Match",
      path: "/jobs",
      priority: "Medium",
    });
  }

  if (latestInterviewScore < 70) {
    nextActions.push({
      title: "Practice interviews",
      description:
        "Improve your interview performance through another AI practice session.",
      action: "Start Interview",
      path: "/interview",
      priority: "Medium",
    });
  }

  if (profileCompleteness < 80) {
    nextActions.push({
      title: "Complete your profile",
      description:
        "A complete profile helps us personalize your career recommendations.",
      action: "Complete Profile",
      path: "/profile",
      priority: "Medium",
    });
  }

  if (completedProfileFields === 0) {
    nextActions.unshift({
      title: "Set up your career profile",
      description:
        "Add your professional information so the platform can personalize your experience.",
      action: "Set Up Profile",
      path: "/profile",
      priority: "High",
    });
  }

  if (nextActions.length === 0) {
    nextActions.push({
      title: "Keep building momentum",
      description:
        "Your career profile is in strong shape. Keep improving and exploring opportunities.",
      action: "Explore Jobs",
      path: "/jobs",
      priority: "Low",
    });
  }

  // =========================================================
  // PROJECT STATISTICS
  // =========================================================

  const totalProjects =
    projects.length;

  const completedProjects =
    projects.filter(
      (project) =>
        project.status === "completed"
    ).length;

  const activeProjects =
    projects.filter(
      (project) =>
        project.status === "in_progress"
    ).length;

  const notStartedProjects =
    projects.filter(
      (project) =>
        project.status === "not_started"
    ).length;

  const projectProgress =
    totalProjects > 0
      ? Math.round(
          projects.reduce(
            (sum, project) =>
              sum +
              (Number(
                project.progress
              ) || 0),
            0
          ) / totalProjects
        )
      : 0;

  // =========================================================
  // PROJECT LIST
  // =========================================================

  const recentProjects = [...projects]
    .sort(
      (a, b) =>
        Number(b?.id || 0) -
        Number(a?.id || 0)
    )
    .slice(0, 4);

  // =========================================================
  // HELPERS
  // =========================================================

  const getProjectStatusLabel =
    (status) => {
      if (status === "completed") {
        return "Completed";
      }

      if (status === "in_progress") {
        return "In Progress";
      }

      return "Not Started";
    };

  const getPriorityClass =
    (priority) => {
      return (
        `dashboard-priority dashboard-priority-${String(
          priority || "medium"
        ).toLowerCase()}`
      );
    };

  const getScoreClass = (
    value
  ) => {
    if (value >= 80) {
      return "score-good";
    }

    if (value >= 60) {
      return "score-medium";
    }

    return "score-low";
  };

  const formatInterviewDate = (
    item
  ) => {
    const date =
      item?.created_at ||
      item?.createdAt ||
      item?.date;

    if (!date) {
      return "Recent session";
    }

    const parsedDate =
      new Date(date);

    if (
      Number.isNaN(
        parsedDate.getTime()
      )
    ) {
      return "Recent session";
    }

    return parsedDate.toLocaleDateString(
      undefined,
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    );
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="dashboard-page">

      {/* =====================================================
          PREMIUM HERO HEADER
      ===================================================== */}

      <section className="dashboard-hero">

        <div className="dashboard-hero-glow dashboard-hero-glow-one" />
        <div className="dashboard-hero-glow dashboard-hero-glow-two" />

        <div className="dashboard-hero-content">

          <div className="dashboard-header-left">

            <div className="dashboard-avatar dashboard-avatar-large">
              {profileImage ? (
                <img
                  src={profileImage}
                  alt={profileName}
                  className="dashboard-avatar-image"
                />
              ) : (
                avatarLetter
              )}
            </div>

            <div className="dashboard-header-copy">

              <div className="dashboard-hero-meta">
                <span className="dashboard-eyebrow">
                  YOUR CAREER WORKSPACE
                </span>

                <span className="dashboard-live-indicator">
                  <span />
                  AI Career Intelligence
                </span>
              </div>

              <h1>
                Welcome back,{" "}
                <span>
                  {profileName}
                </span>
              </h1>

              <p>
                Track your progress,
                strengthen your profile,
                and move closer to your target role.
              </p>

            </div>

          </div>

          <div className="dashboard-header-actions">

            <button
              type="button"
              className="dashboard-secondary-button"
              onClick={() =>
                navigate("/profile")
              }
            >
              Edit Profile
            </button>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Analyze a Job
              <span>→</span>
            </button>

          </div>

        </div>

        <div className="dashboard-hero-snapshot">

          <div className="dashboard-hero-snapshot-label">
            <span>
              CURRENT CAREER SIGNAL
            </span>

            <strong>
              {readinessScore}
              <small>/100</small>
            </strong>
          </div>

          <div className="dashboard-hero-snapshot-progress">
            <div
              style={{
                width: `${readinessScore}%`,
              }}
            />
          </div>

          <div className="dashboard-hero-snapshot-footer">
            <span>
              {readinessLabel}
            </span>

            <span>
              {readinessMomentum}
            </span>
          </div>

        </div>

      </section>

      {/* =====================================================
          PROFILE SUMMARY
      ===================================================== */}

      <section className="dashboard-profile-card">

        <div className="dashboard-profile-main">

          <div className="dashboard-profile-avatar">
            {profileImage ? (
              <img
                src={profileImage}
                alt={profileName}
                className="dashboard-profile-avatar-image"
              />
            ) : (
              avatarLetter
            )}
          </div>

          <div className="dashboard-profile-info">

            <div className="dashboard-profile-name-row">

              <h2>
                {profileName}
              </h2>

              <span className="dashboard-profile-status">
                Career Profile
              </span>

            </div>

            <p>
              {careerGoal}
            </p>

            {profileLocation && (
              <span className="dashboard-location">
                <span>⌖</span>
                {profileLocation}
              </span>
            )}

          </div>

        </div>

        <div className="dashboard-profile-completeness">

          <div className="dashboard-profile-completeness-top">

            <div>
              <span>
                Profile completeness
              </span>

              <small>
                {completedProfileFields} of{" "}
                {profileFields.length} fields
              </small>
            </div>

            <strong>
              {profileCompleteness}%
            </strong>

          </div>

          <div className="dashboard-small-progress">
            <div
              style={{
                width: `${profileCompleteness}%`,
              }}
            />
          </div>

          <button
            type="button"
            onClick={() =>
              navigate("/profile")
            }
          >
            Complete Profile
            <span>→</span>
          </button>

        </div>

      </section>

      {/* =====================================================
          CAREER READINESS
      ===================================================== */}

      <section
        className={`dashboard-readiness dashboard-readiness-${readinessTone}`}
      >

        <div className="dashboard-readiness-main">

          <div className="dashboard-readiness-score">

            <div
              className="dashboard-readiness-circle"
              style={{
                "--readiness":
                  readinessScore,
              }}
            >

              <div className="dashboard-readiness-circle-inner">

                <span className="dashboard-score-overline">
                  READY
                </span>

                <strong>
                  {readinessScore}
                </strong>

                <span>
                  /100
                </span>

              </div>

            </div>

          </div>

          <div className="dashboard-readiness-content">

            <span className="dashboard-section-eyebrow">
              CAREER READINESS
            </span>

            <div className="dashboard-readiness-title-row">

              <h2>
                {readinessLabel}
              </h2>

              <span className="dashboard-readiness-badge">
                {readinessScore >= 85
                  ? "Excellent"
                  : readinessScore >= 70
                  ? "Strong"
                  : readinessScore >= 50
                  ? "Developing"
                  : "Building"}
              </span>

            </div>

            <p>
              {readinessDescription}
            </p>

            <div className="dashboard-readiness-insight">

              <span className="dashboard-insight-icon">
                AI
              </span>

              <div>
                <strong>
                  Your biggest opportunity
                </strong>

                <span>
                  {careerFocus} is currently at{" "}
                  {careerFocusValue}% and has the
                  highest potential impact on your
                  readiness.
                </span>
              </div>

            </div>

            <div className="dashboard-readiness-actions">

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={() =>
                  navigate("/jobs")
                }
              >
                Improve My Readiness
                <span>→</span>
              </button>

              <button
                type="button"
                className="dashboard-link-button"
                onClick={() =>
                  navigate("/tailored-cv")
                }
              >
                Tailor My CV →
              </button>

            </div>

          </div>

        </div>

        <div className="dashboard-readiness-breakdown">

          <div className="dashboard-breakdown-heading">

            <div>
              <span>
                Readiness breakdown
              </span>

              <small>
                Weighted score
              </small>
            </div>

            <span className="dashboard-breakdown-best">
              Strongest:{" "}
              {strongestSignal?.shortLabel}
            </span>

          </div>

          <div className="dashboard-breakdown-list">

            {readinessBreakdown.map(
              (item) => (
                <div
                  className="dashboard-breakdown-item"
                  key={item.label}
                >

                  <div className="dashboard-breakdown-top">

                    <div>
                      <span>
                        {item.label}
                      </span>

                      <small>
                        {item.weight}
                      </small>
                    </div>

                    <strong>
                      {Math.round(
                        item.value
                      )}
                    </strong>

                  </div>

                  <div className="dashboard-breakdown-bar">

                    <div
                      className={`dashboard-breakdown-fill ${getScoreClass(
                        item.value
                      )}`}
                      style={{
                        width: `${Math.min(
                          item.value,
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>
              )
            )}

          </div>

        </div>

      </section>

      {/* =====================================================
          CAREER SNAPSHOT
      ===================================================== */}

      <section className="dashboard-snapshot-grid">

        {dashboardStats.map(
          (stat, index) => (
            <article
              className={`dashboard-snapshot-card dashboard-snapshot-${stat.tone}`}
              key={stat.label}
            >

              <span className="dashboard-snapshot-index">
                0{index + 1}
              </span>

              <div className="dashboard-snapshot-value">
                {stat.value}
              </div>

              <div className="dashboard-snapshot-copy">

                <strong>
                  {stat.label}
                </strong>

                <span>
                  {stat.detail}
                </span>

              </div>

            </article>
          )
        )}

      </section>

      {/* =====================================================
          NEXT BEST ACTIONS
      ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              AI GUIDANCE
            </span>

            <h2>
              Your Next Best Actions
            </h2>

            <p>
              Focus on the actions that can
              improve your career readiness most.
            </p>
          </div>

          <span className="dashboard-ai-badge">
            <span />
            AI
          </span>

        </div>

        <div className="dashboard-actions-grid">

          {nextActions
            .slice(0, 4)
            .map(
              (item, index) => (
                <article
                  className="dashboard-action-card"
                  key={`${item.title}-${index}`}
                >

                  <div className="dashboard-action-top">

                    <div className="dashboard-action-number">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <span
                      className={getPriorityClass(
                        item.priority
                      )}
                    >
                      {item.priority}
                    </span>

                  </div>

                  <h3>
                    {item.title}
                  </h3>

                  <p>
                    {item.description}
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      navigate(
                        item.path
                      )
                    }
                  >
                    {item.action}
                    <span>
                      →
                    </span>
                  </button>

                </article>
              )
            )}

        </div>

      </section>

      {/* =====================================================
          CAREER SIGNALS
      ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              CAREER SIGNALS
            </span>

            <h2>
              Your Key Metrics
            </h2>

            <p>
              The core indicators behind your
              current career position.
            </p>
          </div>

        </div>

        <div className="dashboard-metrics-grid">

          <article className="dashboard-metric-card">

            <div className="dashboard-metric-icon">
              CV
            </div>

            <div className="dashboard-metric-content">
              <span>
                CV Score
              </span>

              <strong>
                {cvScore}
                <small>/100</small>
              </strong>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/cv")
              }
            >
              Review
              <span>→</span>
            </button>

          </article>

          <article className="dashboard-metric-card">

            <div className="dashboard-metric-icon">
              JM
            </div>

            <div className="dashboard-metric-content">
              <span>
                Latest Job Match
              </span>

              <strong>
                {jobMatch}
                <small>%</small>
              </strong>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Analyze
              <span>→</span>
            </button>

          </article>

          <article className="dashboard-metric-card">

            <div className="dashboard-metric-icon">
              IV
            </div>

            <div className="dashboard-metric-content">
              <span>
                Interview Score
              </span>

              <strong>
                {latestInterviewScore}
                <small>/100</small>
              </strong>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/interview")
              }
            >
              Practice
              <span>→</span>
            </button>

          </article>

          <article className="dashboard-metric-card">

            <div className="dashboard-metric-icon">
              SK
            </div>

            <div className="dashboard-metric-content">
              <span>
                Skill Alignment
              </span>

              <strong>
                {skillAlignment}
                <small>%</small>
              </strong>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Improve
              <span>→</span>
            </button>

          </article>

          <article className="dashboard-metric-card">

            <div className="dashboard-metric-icon">
              PF
            </div>

            <div className="dashboard-metric-content">
              <span>
                Profile
              </span>

              <strong>
                {profileCompleteness}
                <small>%</small>
              </strong>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/profile")
              }
            >
              Complete
              <span>→</span>
            </button>

          </article>

        </div>

      </section>

      {/* =====================================================
          SKILLS + SKILL GAPS
      ===================================================== */}

      <div className="dashboard-two-column">

        <section className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <span className="dashboard-section-eyebrow">
                CURRENT CAPABILITIES
              </span>

              <h2>
                My Skills
              </h2>

              <p>
                Skills detected from your CV
                and career data.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/cv")
              }
            >
              View CV →
            </button>

          </div>

          <div className="dashboard-panel-stat-row">

            <div>
              <strong>
                {detectedSkillCount}
              </strong>

              <span>
                detected skills
              </span>
            </div>

            {requiredSkillCount > 0 && (
              <div>
                <strong>
                  {matchedSkillCount}
                </strong>

                <span>
                  matched skills
                </span>
              </div>
            )}

          </div>

          {skills.length > 0 ? (
            <div className="dashboard-skill-cloud">

              {skills.map(
                (skill, index) => (
                  <span
                    className="dashboard-skill-pill"
                    key={`${skill}-${index}`}
                  >
                    {skill}
                  </span>
                )
              )}

            </div>
          ) : (
            <div className="dashboard-empty-inline">

              <strong>
                No skills detected yet.
              </strong>

              <span>
                Upload a CV so the platform
                can analyze your current skills.
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/cv")
                }
              >
                Upload CV →
              </button>

            </div>
          )}

        </section>

        <section className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <span className="dashboard-section-eyebrow">
                OPPORTUNITY GAPS
              </span>

              <h2>
                Skill Gaps
              </h2>

              <p>
                Skills that may be missing for
                your latest target role.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Analyze →
            </button>

          </div>

          <div className="dashboard-panel-stat-row">

            <div>
              <strong>
                {skillGapCount}
              </strong>

              <span>
                identified gaps
              </span>
            </div>

            <div>
              <strong>
                {skillAlignment}%
              </strong>

              <span>
                current alignment
              </span>
            </div>

          </div>

          {missingSkills.length > 0 ? (
            <div className="dashboard-skill-cloud">

              {missingSkills.map(
                (skill, index) => (
                  <span
                    className="dashboard-gap-pill"
                    key={`${skill}-${index}`}
                  >
                    <span>
                      +
                    </span>

                    {skill}
                  </span>
                )
              )}

            </div>
          ) : (
            <div className="dashboard-empty-inline dashboard-empty-success">

              <strong>
                No major gaps detected.
              </strong>

              <span>
                Analyze another job to discover
                new opportunities for growth.
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/jobs")
                }
              >
                Analyze a Job →
              </button>

            </div>
          )}

        </section>

      </div>

      {/* =====================================================
          LEARNING ROADMAP
      ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              PERSONALIZED LEARNING
            </span>

            <h2>
              Learning Roadmap
            </h2>

            <p>
              A suggested learning path based
              on your identified skill gaps.
            </p>
          </div>

          <button
            type="button"
            className="dashboard-text-action"
            onClick={() =>
              navigate("/jobs")
            }
          >
            Refresh Roadmap →
          </button>

        </div>

        {roadmap.length > 0 ? (
          <div className="dashboard-roadmap">

            {roadmap.map(
              (item, index) => (
                <article
                  className="dashboard-roadmap-item"
                  key={`${item.skill || "skill"}-${index}`}
                >

                  <div className="dashboard-roadmap-step">

                    <span>
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </span>

                  </div>

                  <div className="dashboard-roadmap-content">

                    <div className="dashboard-roadmap-heading">

                      <div>
                        <span className="dashboard-roadmap-label">
                          STEP{" "}
                          {String(
                            index + 1
                          ).padStart(2, "0")}
                        </span>

                        <h3>
                          {item.skill ||
                            "Skill Development"}
                        </h3>
                      </div>

                      <span className="dashboard-roadmap-priority">
                        {item.priority ||
                          "Medium"}
                      </span>

                    </div>

                    {Array.isArray(
                      item.steps
                    ) &&
                    item.steps.length > 0 ? (
                      <ol>
                        {item.steps.map(
                          (
                            step,
                            stepIndex
                          ) => (
                            <li
                              key={`${item.skill}-${stepIndex}`}
                            >
                              <span>
                                {String(
                                  stepIndex + 1
                                ).padStart(
                                  2,
                                  "0"
                                )}
                              </span>

                              {step}
                            </li>
                          )
                        )}
                      </ol>
                    ) : (
                      <p>
                        Build practical
                        knowledge in this skill
                        through focused learning
                        and project work.
                      </p>
                    )}

                  </div>

                </article>
              )
            )}

          </div>
        ) : (
          <div className="dashboard-roadmap-empty">

            <div className="dashboard-roadmap-empty-icon">
              →
            </div>

            <div>
              <h3>
                Your roadmap will appear here
              </h3>

              <p>
                Analyze a real job to identify
                skill gaps and generate a
                personalized learning path.
              </p>
            </div>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Find My Skill Gaps
              <span>→</span>
            </button>

          </div>
        )}

      </section>

      {/* =====================================================
          PERSONAL CAREER PLAN
      ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              CAREER ROADMAP
            </span>

            <h2>
              Personal Career Plan
            </h2>

            <p>
              A practical path from your current
              position to job readiness.
            </p>
          </div>

        </div>

        <div className="dashboard-career-plan">

          <article className="dashboard-career-phase">

            <div className="dashboard-phase-marker">
              1
            </div>

            <div className="dashboard-phase-content">

              <div className="dashboard-phase-top">

                <div>
                  <span>
                    PHASE 01
                  </span>

                  <h3>
                    Strengthen Your Foundation
                  </h3>
                </div>

                <span className="dashboard-phase-status">
                  Foundation
                </span>

              </div>

              <p>
                Make sure your profile and CV
                clearly represent your current
                abilities.
              </p>

              <ul>
                <li>
                  <span>✓</span>
                  Complete your professional profile
                </li>

                <li>
                  <span>✓</span>
                  Improve your CV structure
                </li>

                <li>
                  <span>✓</span>
                  Add projects and certifications
                </li>
              </ul>

            </div>

          </article>

          <article className="dashboard-career-phase">

            <div className="dashboard-phase-marker">
              2
            </div>

            <div className="dashboard-phase-content">

              <div className="dashboard-phase-top">

                <div>
                  <span>
                    PHASE 02
                  </span>

                  <h3>
                    Close Your Skill Gaps
                  </h3>
                </div>

                <span className="dashboard-phase-status">
                  Learning
                </span>

              </div>

              {missingSkills.length > 0 ? (
                <>
                  <p>
                    Focus on the skills most
                    important for your target role.
                  </p>

                  <div className="dashboard-career-skills">

                    {missingSkills
                      .slice(0, 8)
                      .map(
                        (skill, index) => (
                          <span
                            key={`${skill}-${index}`}
                          >
                            {skill}
                          </span>
                        )
                      )}

                  </div>
                </>
              ) : (
                <p>
                  No major skill gaps detected yet.
                  Keep validating your profile
                  against real opportunities.
                </p>
              )}

            </div>

          </article>

          <article className="dashboard-career-phase">

            <div className="dashboard-phase-marker">
              3
            </div>

            <div className="dashboard-phase-content">

              <div className="dashboard-phase-top">

                <div>
                  <span>
                    PHASE 03
                  </span>

                  <h3>
                    Build Practical Experience
                  </h3>
                </div>

                <span className="dashboard-phase-status">
                  Practice
                </span>

              </div>

              <p>
                Turn your skills into real
                evidence that employers can evaluate.
              </p>

              <ul>

                {missingSkills.length > 0 ? (
                  <>
                    <li>
                      <span>→</span>
                      Build a project using{" "}
                      {missingSkills[0]}
                    </li>

                    {missingSkills[1] && (
                      <li>
                        <span>→</span>
                        Build a second project using{" "}
                        {missingSkills[1]}
                      </li>
                    )}

                    <li>
                      <span>→</span>
                      Add your projects to your CV
                    </li>
                  </>
                ) : (
                  <>
                    <li>
                      <span>→</span>
                      Build one strong portfolio project
                    </li>

                    <li>
                      <span>→</span>
                      Publish it on GitHub
                    </li>

                    <li>
                      <span>→</span>
                      Add it to your CV
                    </li>
                  </>
                )}

              </ul>

              <button
                type="button"
                className="dashboard-secondary-button"
                onClick={() =>
                  navigate("/projects")
                }
              >
                Manage Projects
                <span>→</span>
              </button>

            </div>

          </article>

          <article className="dashboard-career-phase">

            <div className="dashboard-phase-marker">
              4
            </div>

            <div className="dashboard-phase-content">

              <div className="dashboard-phase-top">

                <div>
                  <span>
                    PHASE 04
                  </span>

                  <h3>
                    Become Job Ready
                  </h3>
                </div>

                <span className="dashboard-phase-status">
                  Career
                </span>

              </div>

              <p>
                Prepare for real applications
                and technical interviews.
              </p>

              <ul>

                <li>
                  <span>→</span>
                  Practice AI mock interviews
                </li>

                <li>
                  <span>→</span>
                  Analyze real job descriptions
                </li>

                <li>
                  <span>→</span>
                  Improve your job match score
                </li>

                <li>
                  <span>→</span>
                  Start applying consistently
                </li>

              </ul>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={() =>
                  navigate("/interview")
                }
              >
                Start Interview Practice
                <span>→</span>
              </button>

            </div>

          </article>

        </div>

      </section>

      {/* =====================================================
          PROJECT PROGRESS
      ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              PRACTICAL EXPERIENCE
            </span>

            <h2>
              Project Progress
            </h2>

            <p>
              Turn learning into practical,
              portfolio-ready evidence.
            </p>
          </div>

          <button
            type="button"
            className="dashboard-text-action"
            onClick={() =>
              navigate("/projects")
            }
          >
            View Projects →
          </button>

        </div>

        {totalProjects === 0 ? (
          <div className="dashboard-project-empty">

            <div className="dashboard-project-empty-icon">
              +
            </div>

            <div>
              <h3>
                Build your first career project
              </h3>

              <p>
                Projects turn skills into evidence
                that recruiters can evaluate.
              </p>
            </div>

            <button
              type="button"
              className="dashboard-primary-button"
              onClick={() =>
                navigate("/projects")
              }
            >
              Find Projects For Me
              <span>→</span>
            </button>

          </div>
        ) : (
          <>

            <div className="dashboard-project-overview">

              <div className="dashboard-project-stat dashboard-project-stat-featured">

                <span>
                  Total Projects
                </span>

                <strong>
                  {totalProjects}
                </strong>

              </div>

              <div className="dashboard-project-stat">

                <span>
                  In Progress
                </span>

                <strong>
                  {activeProjects}
                </strong>

              </div>

              <div className="dashboard-project-stat">

                <span>
                  Completed
                </span>

                <strong>
                  {completedProjects}
                </strong>

              </div>

              <div className="dashboard-project-stat">

                <span>
                  Not Started
                </span>

                <strong>
                  {notStartedProjects}
                </strong>

              </div>

              <div className="dashboard-project-stat">

                <span>
                  Overall Progress
                </span>

                <strong>
                  {projectProgress}%
                </strong>

              </div>

            </div>

            <div className="dashboard-project-progress-card">

              <div className="dashboard-project-progress-heading">

                <div>
                  <strong>
                    Portfolio progress
                  </strong>

                  <span>
                    Average completion across all
                    your career projects.
                  </span>
                </div>

                <strong>
                  {projectProgress}%
                </strong>

              </div>

              <div className="dashboard-large-progress">

                <div
                  style={{
                    width: `${Math.min(
                      Math.max(
                        projectProgress,
                        0
                      ),
                      100
                    )}%`,
                  }}
                />

              </div>

            </div>

            <div className="dashboard-project-list">

              {recentProjects.map(
                (project) => {
                  const progress =
                    Math.min(
                      Math.max(
                        Number(
                          project.progress
                        ) || 0,
                        0
                      ),
                      100
                    );

                  return (
                    <article
                      className="dashboard-project-row"
                      key={project.id}
                    >

                      <div className="dashboard-project-row-main">

                        <div className="dashboard-project-dot">
                          {project.status ===
                          "completed"
                            ? "✓"
                            : "•"}
                        </div>

                        <div>
                          <strong>
                            {project.title}
                          </strong>

                          <span>
                            {getProjectStatusLabel(
                              project.status
                            )}
                          </span>
                        </div>

                      </div>

                      <div className="dashboard-project-row-progress">

                        <div className="dashboard-mini-progress">

                          <div
                            style={{
                              width: `${progress}%`,
                            }}
                          />

                        </div>

                        <strong>
                          {progress}%
                        </strong>

                      </div>

                    </article>
                  );
                }
              )}

            </div>

          </>
        )}

      </section>

      {/* =====================================================
          RECENT JOBS + INTERVIEWS
      ===================================================== */}

      <div className="dashboard-two-column">

        <section className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <span className="dashboard-section-eyebrow">
                OPPORTUNITIES
              </span>

              <h2>
                Recent Job Analyses
              </h2>

              <p>
                Your latest job matching results.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/jobs")
              }
            >
              Job Matcher →
            </button>

          </div>

          {jobHistory.length > 0 ? (
            <div className="dashboard-history-list">

              {jobHistory
                .slice(0, 5)
                .map(
                  (job, index) => (
                    <div
                      className="dashboard-history-item"
                      key={
                        job.id ??
                        `${job.cv_id}-${index}`
                      }
                    >

                      <div className="dashboard-history-icon">
                        JM
                      </div>

                      <div className="dashboard-history-content">

                        <strong>
                          Job Analysis #{job.id}
                        </strong>

                        {job.cv_id && (
                          <span>
                            CV ID: {job.cv_id}
                          </span>
                        )}

                      </div>

                      <strong
                        className={`dashboard-history-score ${getScoreClass(
                          Number(
                            job.score
                          ) || 0
                        )}`}
                      >
                        {job.score ?? 0}%
                      </strong>

                    </div>
                  )
                )}

            </div>
          ) : (
            <div className="dashboard-empty-inline">

              <strong>
                No job analyses yet.
              </strong>

              <span>
                Analyze real job descriptions to
                understand where you stand.
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/jobs")
                }
              >
                Analyze a Job →
              </button>

            </div>
          )}

        </section>

        <section className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <span className="dashboard-section-eyebrow">
                INTERVIEW PRACTICE
              </span>

              <h2>
                Recent Interviews
              </h2>

              <p>
                Your latest AI interview practice.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate("/interview")
              }
            >
              Practice →
            </button>

          </div>

          {sortedInterviews.length > 0 ? (
            <div className="dashboard-history-list">

              {sortedInterviews
                .slice(0, 5)
                .map(
                  (interview, index) => {
                    const score =
                      Number(
                        interview.score
                      ) || 0;

                    return (
                      <div
                        className="dashboard-history-item"
                        key={
                          interview.id ??
                          `${interview.role}-${index}`
                        }
                      >

                        <div className="dashboard-history-icon">
                          IV
                        </div>

                        <div className="dashboard-history-content">

                          <strong>
                            {interview.role ||
                              "General Interview"}
                          </strong>

                          <span>
                            {formatInterviewDate(
                              interview
                            )}
                            {interview.total_questions !=
                              null &&
                              ` · ${interview.total_questions} questions`}
                          </span>

                        </div>

                        <strong
                          className={`dashboard-history-score ${getScoreClass(
                            score
                          )}`}
                        >
                          {score}/100
                        </strong>

                      </div>
                    );
                  }
                )}

            </div>
          ) : (
            <div className="dashboard-empty-inline">

              <strong>
                No completed interviews yet.
              </strong>

              <span>
                Practice with the AI simulator to
                improve your interview confidence.
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/interview")
                }
              >
                Start Interview →
              </button>

            </div>
          )}

        </section>

      </div>

      {/* =====================================================
          QUICK ACTIONS
      ===================================================== */}

      <section className="dashboard-section dashboard-quick-actions-section">

        <div className="dashboard-section-header">

          <div>
            <span className="dashboard-section-eyebrow">
              CAREER TOOLS
            </span>

            <h2>
              Quick Actions
            </h2>

            <p>
              Continue building your career from
              wherever you are.
            </p>
          </div>

        </div>

        <div className="dashboard-quick-actions">

          <button
            type="button"
            onClick={() =>
              navigate("/cv")
            }
          >
            <span className="dashboard-quick-icon">
              CV
            </span>

            <span>
              <strong>
                My CV
              </strong>

              <small>
                Review and analyze your CV
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/cv-builder")
            }
          >
            <span className="dashboard-quick-icon">
              CB
            </span>

            <span>
              <strong>
                CV Builder
              </strong>

              <small>
                Build a professional CV
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/tailored-cv")
            }
          >
            <span className="dashboard-quick-icon">
              AI
            </span>

            <span>
              <strong>
                Tailored CV
              </strong>

              <small>
                Adapt your CV to a job
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/projects")
            }
          >
            <span className="dashboard-quick-icon">
              PJ
            </span>

            <span>
              <strong>
                My Projects
              </strong>

              <small>
                Build practical experience
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/portfolio")
            }
          >
            <span className="dashboard-quick-icon">
              PF
            </span>

            <span>
              <strong>
                Portfolio
              </strong>

              <small>
                Showcase your achievements
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/chat")
            }
          >
            <span className="dashboard-quick-icon">
              AI
            </span>

            <span>
              <strong>
                AI Career Assistant
              </strong>

              <small>
                Get personalized guidance
              </small>
            </span>

            <b>
              →
            </b>
          </button>

          <button
            type="button"
            onClick={() =>
              navigate("/interview")
            }
          >
            <span className="dashboard-quick-icon">
              IV
            </span>

            <span>
              <strong>
                Interview Simulator
              </strong>

              <small>
                Practice for real interviews
              </small>
            </span>

            <b>
              →
            </b>
          </button>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;