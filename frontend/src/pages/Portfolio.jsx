import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getCareerProjects,
  getProfile,
} from "../services/api";

import "./Portfolio.css";

function Portfolio() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [profile, setProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retrying, setRetrying] = useState(false);

  /* =========================================================
     LOAD PORTFOLIO
     ========================================================= */

  const loadPortfolio = async ({
    isRetry = false,
  } = {}) => {
    try {
      if (isRetry) {
        setRetrying(true);
      } else {
        setLoading(true);
      }

      setError("");

      const [
        projectData,
        profileData,
      ] = await Promise.all([
        getCareerProjects(),
        getProfile(),
      ]);

      const completedProjects =
        Array.isArray(projectData)
          ? projectData.filter(
              (project) =>
                project?.status ===
                "completed"
            )
          : [];

      setProjects(completedProjects);
      setProfile(profileData || null);
    } catch (err) {
      setError(
        err?.message ||
          "Failed to load portfolio."
      );
    } finally {
      setLoading(false);
      setRetrying(false);
    }
  };

  useEffect(() => {
    loadPortfolio();
  }, []);

  /* =========================================================
     PROFILE DATA
     ========================================================= */

  const displayName =
    profile?.full_name?.trim() ||
    "Career Explorer";

  const careerGoal =
    profile?.career_goal?.trim() ||
    "AI / Full Stack Developer";

  const location =
    profile?.location?.trim() || "";

  const linkedin =
    profile?.linkedin_url?.trim() || "";

  const bio =
    profile?.bio?.trim() || "";

  const avatarLetter =
    displayName.charAt(0).toUpperCase() ||
    "A";

  /* =========================================================
     PROJECT STATISTICS
     ========================================================= */

  const totalProjects = projects.length;

  const totalSkills = useMemo(() => {
    const skillMap = new Map();

    projects.forEach((project) => {
      const skills = Array.isArray(
        project?.skills
      )
        ? project.skills
        : [];

      skills.forEach((skill) => {
        if (!skill) return;

        const normalized =
          String(skill).trim();

        if (!normalized) return;

        const key =
          normalized.toLowerCase();

        if (!skillMap.has(key)) {
          skillMap.set(
            key,
            normalized
          );
        }
      });
    });

    return Array.from(
      skillMap.values()
    ).sort((a, b) =>
      a.localeCompare(b)
    );
  }, [projects]);

  const totalObjectives = useMemo(() => {
    return projects.reduce(
      (total, project) => {
        const objectives =
          Array.isArray(
            project?.objectives
          )
            ? project.objectives
            : [];

        return (
          total + objectives.length
        );
      },
      0
    );
  }, [projects]);

  const totalGithubProjects =
    projects.filter(
      (project) =>
        Boolean(
          project?.github_url
        )
    ).length;

  const totalDemoProjects =
    projects.filter(
      (project) =>
        Boolean(
          project?.demo_url
        )
    ).length;

  const portfolioStatus =
    totalProjects >= 3
      ? "Strong"
      : totalProjects > 0
      ? "Growing"
      : "Starting";

  const portfolioStatusDescription =
    totalProjects >= 3
      ? "Your portfolio shows meaningful hands-on experience."
      : totalProjects > 0
      ? "You have started building evidence of your skills."
      : "Complete your first project to start building your portfolio.";

  /* =========================================================
     HELPERS
     ========================================================= */

  const getDifficultyClass = (
    difficulty
  ) => {
    const value =
      String(
        difficulty ||
          "Intermediate"
      ).toLowerCase();

    if (value.includes("beginner")) {
      return "beginner";
    }

    if (
      value.includes("advanced") ||
      value.includes("expert")
    ) {
      return "advanced";
    }

    return "intermediate";
  };

  const getProjectProgress = (
    project
  ) => {
    const progress =
      Number(project?.progress);

    if (
      Number.isFinite(progress)
    ) {
      return Math.max(
        0,
        Math.min(100, progress)
      );
    }

    return project?.status ===
      "completed"
      ? 100
      : 0;
  };

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-loading">
          <div className="portfolio-loading-spinner" />

          <p>
            Preparing your portfolio...
          </p>
        </div>
      </div>
    );
  }

  /* =========================================================
     ERROR
     ========================================================= */

  if (error) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-error">
          <div className="portfolio-error-icon">
            !
          </div>

          <span className="portfolio-eyebrow">
            PORTFOLIO
          </span>

          <h2>
            Unable to load portfolio
          </h2>

          <p>
            {error}
          </p>

          <button
            className="primary-button"
            onClick={() =>
              loadPortfolio({
                isRetry: true,
              })
            }
            disabled={retrying}
          >
            {retrying
              ? "Retrying..."
              : "Try Again"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-page">
      {/* =====================================================
          HERO
          ===================================================== */}

      <section className="portfolio-hero">
        <div className="portfolio-hero-left">
          <div className="portfolio-avatar">
            {avatarLetter}
          </div>

          <div className="portfolio-hero-content">
            <span className="portfolio-eyebrow">
              PROFESSIONAL PORTFOLIO
            </span>

            <h1>
              {displayName}
            </h1>

            <p className="portfolio-role">
              {careerGoal}
            </p>

            {location && (
              <p className="portfolio-location">
                <span>📍</span>
                {location}
              </p>
            )}

            <div className="portfolio-status">
              <span className="portfolio-status-dot" />

              <span>
                {portfolioStatus}
                {" "}Portfolio
              </span>
            </div>
          </div>
        </div>

        <div className="portfolio-hero-actions">
          {linkedin && (
            <a
              href={linkedin}
              target="_blank"
              rel="noreferrer"
              className="secondary-button"
            >
              LinkedIn
              <span>↗</span>
            </a>
          )}

          <button
            className="primary-button"
            onClick={() =>
              navigate("/projects")
            }
          >
            Manage Projects
            <span>→</span>
          </button>
        </div>
      </section>

      {/* =====================================================
          PORTFOLIO SUMMARY
          ===================================================== */}

      <section className="portfolio-stats">
        <div className="portfolio-stat">
          <span>
            Completed Projects
          </span>

          <strong>
            {totalProjects}
          </strong>

          <small>
            Real projects showcased
          </small>
        </div>

        <div className="portfolio-stat">
          <span>
            Skills Demonstrated
          </span>

          <strong>
            {totalSkills.length}
          </strong>

          <small>
            Across completed work
          </small>
        </div>

        <div className="portfolio-stat">
          <span>
            Project Outcomes
          </span>

          <strong>
            {totalObjectives}
          </strong>

          <small>
            Defined objectives delivered
          </small>
        </div>

        <div className="portfolio-stat">
          <span>
            Portfolio Status
          </span>

          <strong>
            {portfolioStatus}
          </strong>

          <small>
            {portfolioStatusDescription}
          </small>
        </div>
      </section>

      {/* =====================================================
          PORTFOLIO INSIGHT
          ===================================================== */}

      <section className="portfolio-insight">
        <div className="portfolio-insight-icon">
          ✦
        </div>

        <div>
          <span className="portfolio-eyebrow">
            PORTFOLIO INSIGHT
          </span>

          <h3>
            Your work is your strongest proof.
          </h3>

          <p>
            A strong portfolio doesn't just
            list technologies. It shows what
            you built, what problems you solved,
            and what outcomes you achieved.
          </p>
        </div>
      </section>

      {/* =====================================================
          ABOUT
          ===================================================== */}

      {bio && (
        <section className="portfolio-about">
          <div className="portfolio-section-label">
            <span className="portfolio-eyebrow">
              ABOUT
            </span>

            <h2>
              About Me
            </h2>
          </div>

          <div className="portfolio-about-content">
            <p>{bio}</p>
          </div>
        </section>
      )}

      {/* =====================================================
          EXPERTISE
          ===================================================== */}

      {totalSkills.length > 0 && (
        <section className="portfolio-skills-section">
          <div className="portfolio-section-heading">
            <div>
              <span className="portfolio-eyebrow">
                EXPERTISE
              </span>

              <h2>
                Skills Demonstrated
              </h2>

              <p>
                Technologies and skills
                demonstrated through
                completed projects.
              </p>
            </div>

            <span className="portfolio-section-count">
              {totalSkills.length} Skills
            </span>
          </div>

          <div className="portfolio-skills">
            {totalSkills.map(
              (skill) => (
                <span
                  key={skill}
                  className="portfolio-skill"
                >
                  <span>✓</span>
                  {skill}
                </span>
              )
            )}
          </div>
        </section>
      )}

      {/* =====================================================
          PROJECTS
          ===================================================== */}

      <section className="portfolio-projects-section">
        <div className="portfolio-section-heading">
          <div>
            <span className="portfolio-eyebrow">
              PROJECTS
            </span>

            <h2>
              Featured Work
            </h2>

            <p>
              Real projects completed as
              part of your career development
              journey.
            </p>
          </div>

          {totalProjects > 0 && (
            <span className="portfolio-section-count">
              {totalProjects}{" "}
              {totalProjects === 1
                ? "Project"
                : "Projects"}
            </span>
          )}
        </div>

        {projects.length === 0 ? (
          <div className="portfolio-empty">
            <div className="portfolio-empty-icon">
              🚀
            </div>

            <span className="portfolio-eyebrow">
              START BUILDING
            </span>

            <h3>
              Your portfolio is waiting
            </h3>

            <p>
              Complete your first career
              project and it will
              automatically appear here.
            </p>

            <button
              className="primary-button"
              onClick={() =>
                navigate("/projects")
              }
            >
              Explore Projects
              <span>→</span>
            </button>
          </div>
        ) : (
          <div className="portfolio-project-grid">
            {projects.map(
              (project) => {
                const progress =
                  getProjectProgress(
                    project
                  );

                const objectives =
                  Array.isArray(
                    project?.objectives
                  )
                    ? project.objectives
                    : [];

                const skills =
                  Array.isArray(
                    project?.skills
                  )
                    ? project.skills
                    : [];

                const difficultyClass =
                  getDifficultyClass(
                    project?.difficulty
                  );

                return (
                  <article
                    className="portfolio-project-card"
                    key={project.id}
                  >
                    {/* PROJECT HEADER */}

                    <div className="portfolio-project-header">
                      <div>
                        <span className="portfolio-completed-badge">
                          <span>✓</span>
                          Completed
                        </span>

                        <h3>
                          {project.title ||
                            "Untitled Project"}
                        </h3>
                      </div>

                      <span
                        className={`portfolio-difficulty ${difficultyClass}`}
                      >
                        {project.difficulty ||
                          "Intermediate"}
                      </span>
                    </div>

                    {/* DESCRIPTION */}

                    <p className="portfolio-project-description">
                      {project.description ||
                        "No project description available."}
                    </p>

                    {/* TARGET ROLE */}

                    {project.target_role && (
                      <div className="portfolio-target-role">
                        <span>
                          Target Role
                        </span>

                        <strong>
                          {
                            project.target_role
                          }
                        </strong>
                      </div>
                    )}

                    {/* SKILLS */}

                    {skills.length > 0 && (
                      <div className="portfolio-project-skills">
                        {skills.map(
                          (skill) => (
                            <span
                              key={skill}
                            >
                              {skill}
                            </span>
                          )
                        )}
                      </div>
                    )}

                    {/* OBJECTIVES */}

                    {objectives.length >
                      0 && (
                      <div className="portfolio-project-objectives">
                        <div className="portfolio-subsection-heading">
                          <h4>
                            Key Outcomes
                          </h4>

                          <span>
                            {objectives.length}
                          </span>
                        </div>

                        <ul>
                          {objectives
                            .slice(0, 4)
                            .map(
                              (
                                objective,
                                index
                              ) => (
                                <li
                                  key={`${objective}-${index}`}
                                >
                                  <span className="objective-check">
                                    ✓
                                  </span>

                                  <span>
                                    {
                                      objective
                                    }
                                  </span>
                                </li>
                              )
                            )}
                        </ul>

                        {objectives.length >
                          4 && (
                          <small className="more-objectives">
                            +
                            {objectives.length -
                              4}{" "}
                            more outcomes
                          </small>
                        )}
                      </div>
                    )}

                    {/* PROGRESS */}

                    <div className="portfolio-project-meta">
                      <div>
                        <span>
                          Completion
                        </span>

                        <strong>
                          {progress}%
                        </strong>
                      </div>

                      <span className="completion-status">
                        Fully Completed
                      </span>
                    </div>

                    <div className="portfolio-progress-bar">
                      <span
                        style={{
                          width: `${progress}%`,
                        }}
                      />
                    </div>

                    {/* LINKS */}

                    <div className="portfolio-project-links">
                      {project.github_url && (
                        <a
                          href={
                            project.github_url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          <span>
                            GitHub
                          </span>

                          <strong>
                            ↗
                          </strong>
                        </a>
                      )}

                      {project.demo_url && (
                        <a
                          href={
                            project.demo_url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          <span>
                            Live Demo
                          </span>

                          <strong>
                            ↗
                          </strong>
                        </a>
                      )}

                      {!project.github_url &&
                        !project.demo_url && (
                          <span className="portfolio-no-links">
                            Add GitHub or Demo from
                            My Projects
                          </span>
                        )}
                    </div>
                  </article>
                );
              }
            )}
          </div>
        )}
      </section>

      {/* =====================================================
          PORTFOLIO FOOTER STATS
          ===================================================== */}

      {totalProjects > 0 && (
        <section className="portfolio-proof">
          <div className="portfolio-proof-item">
            <span>
              Projects with GitHub
            </span>

            <strong>
              {totalGithubProjects}
            </strong>
          </div>

          <div className="portfolio-proof-item">
            <span>
              Projects with Live Demo
            </span>

            <strong>
              {totalDemoProjects}
            </strong>
          </div>

          <div className="portfolio-proof-item">
            <span>
              Skills across projects
            </span>

            <strong>
              {totalSkills.length}
            </strong>
          </div>
        </section>
      )}

      {/* =====================================================
          CALL TO ACTION
          ===================================================== */}

      <section className="portfolio-cta">
        <div>
          <span className="portfolio-eyebrow">
            KEEP BUILDING
          </span>

          <h2>
            Turn your skills into evidence.
          </h2>

          <p>
            Complete more projects to make
            your portfolio stronger, demonstrate
            your capabilities, and improve your
            career readiness.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() =>
            navigate("/projects")
          }
        >
          Build Another Project
          <span>→</span>
        </button>
      </section>
    </div>
  );
}

export default Portfolio;