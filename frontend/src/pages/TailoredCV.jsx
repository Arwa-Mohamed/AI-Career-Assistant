import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { getCVs } from "../services/api";

import {
  tailorCV,
  generateTailoredCVPDF,
} from "../services/tailoredCVApi";

import "./TailoredCV.css";

function TailoredCV() {
  const [cvs, setCVs] = useState([]);

  const [jobTitle, setJobTitle] =
    useState("");

  const [
    jobDescription,
    setJobDescription,
  ] = useState("");

  const [
    requiredSkills,
    setRequiredSkills,
  ] = useState("");

  const [selectedCV, setSelectedCV] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [
    generatingPDF,
    setGeneratingPDF,
  ] = useState(false);

  const [error, setError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  /* =========================================================
     LOAD CVS
     ========================================================= */

  useEffect(() => {
    loadCVs();
  }, []);

  const loadCVs = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getCVs();

      const normalized = Array.isArray(
        data
      )
        ? data
        : [];

      setCVs(normalized);

      if (normalized.length > 0) {
        setSelectedCV(
          String(normalized[0].id)
        );
      }
    } catch (err) {
      setError(
        err?.message ||
          "Failed to load your CVs."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     DERIVED DATA
     ========================================================= */

  const selectedCVObject = useMemo(
    () =>
      cvs.find(
        (cv) =>
          String(cv.id) ===
          String(selectedCV)
      ),
    [cvs, selectedCV]
  );

  const requiredSkillList = useMemo(
    () =>
      requiredSkills
        .split(",")
        .map((skill) =>
          skill.trim()
        )
        .filter(Boolean),
    [requiredSkills]
  );

  const matchedSkills =
    Array.isArray(
      result?.skills?.matched_skills
    )
      ? result.skills.matched_skills
      : [];

  const missingSkills =
    Array.isArray(
      result?.skills?.missing_skills
    )
      ? result.skills.missing_skills
      : [];

  const recommendedProjects =
    Array.isArray(
      result?.recommended_projects
    )
      ? result.recommended_projects
      : [];

  const matchScore =
    Number(result?.match?.score) ||
    0;

  const skillMatchScore =
    Number(
      result?.match
        ?.skill_match_score
    ) || 0;

  const jobDescriptionLength =
    jobDescription.length;

  const jobDescriptionWords =
    jobDescription.trim()
      ? jobDescription
          .trim()
          .split(/\s+/)
          .filter(Boolean).length
      : 0;

  const matchLabel =
    matchScore >= 85
      ? "Excellent Fit"
      : matchScore >= 70
      ? "Strong Fit"
      : matchScore >= 50
      ? "Moderate Fit"
      : "Needs Improvement";

  const matchDescription =
    matchScore >= 85
      ? "Your CV is highly aligned with this role."
      : matchScore >= 70
      ? "Your CV is a strong match with a few areas to improve."
      : matchScore >= 50
      ? "Your profile has partial alignment with this opportunity."
      : "There are important gaps between your CV and this role.";

  const formReady =
    jobTitle.trim().length > 0 &&
    jobDescription.trim().length >= 30 &&
    Boolean(selectedCV) &&
    !analyzing;

  /* =========================================================
     ANALYZE & TAILOR
     ========================================================= */

  const handleAnalyze = async (
    event
  ) => {
    event.preventDefault();

    setError("");
    setSuccessMessage("");

    if (!jobTitle.trim()) {
      setError(
        "Please enter the job title."
      );
      return;
    }

    if (!jobDescription.trim()) {
      setError(
        "Please enter the job description."
      );
      return;
    }

    if (
      jobDescription.trim().length <
      30
    ) {
      setError(
        "Please paste a more complete job description for a better analysis."
      );
      return;
    }

    if (!selectedCV) {
      setError(
        "Please select a source CV."
      );
      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setSuccessMessage("");
      setResult(null);

      const data = await tailorCV({
        jobTitle:
          jobTitle.trim(),

        jobDescription:
          jobDescription.trim(),

        requiredSkills:
          requiredSkillList,

        cvId: selectedCV
          ? Number(selectedCV)
          : null,
      });

      setResult(data);

      setSuccessMessage(
        "Your tailored CV analysis is ready."
      );
    } catch (err) {
      setError(
        err?.message ||
          "Failed to analyze the job."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  /* =========================================================
     GENERATE TAILORED PDF
     ========================================================= */

  const handleGenerateTailoredPDF =
    async () => {
      if (!result) {
        setError(
          "Please analyze a job before generating a tailored CV."
        );
        return;
      }

      try {
        setGeneratingPDF(true);
        setError("");
        setSuccessMessage("");

        const recommendedProjectIds =
          recommendedProjects
            .map(
              (project) =>
                project.id
            )
            .filter(Boolean);

        await generateTailoredCVPDF({
          jobTitle:
            result?.job?.title ||
            jobTitle.trim(),

          tailoredSummary:
            result?.tailored_summary ||
            "",

          matchedSkills:
            matchedSkills,

          recommendedProjectIds,

          cvId: selectedCV
            ? Number(selectedCV)
            : null,
        });

        setSuccessMessage(
          "Tailored CV PDF generated successfully."
        );
      } catch (err) {
        setError(
          err?.message ||
            "Failed to generate tailored CV."
        );
      } finally {
        setGeneratingPDF(false);
      }
    };

  /* =========================================================
     RESET ANALYSIS
     ========================================================= */

  const handleReset = () => {
    setResult(null);
    setError("");
    setSuccessMessage("");
  };

  /* =========================================================
     SCORE CLASS
     ========================================================= */

  const getScoreClass = (score) => {
    if (score >= 85) {
      return "excellent";
    }

    if (score >= 70) {
      return "strong";
    }

    if (score >= 50) {
      return "moderate";
    }

    return "low";
  };

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <div className="tailored-loading">
        <div className="tailored-loader" />

        <span className="tailored-loading-kicker">
          AI CAREER TOOLS
        </span>

        <h2>
          Preparing Tailored CV
        </h2>

        <p>
          Loading your career data...
        </p>
      </div>
    );
  }

  /* =========================================================
     MAIN
     ========================================================= */

  return (
    <div className="tailored-page">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="tailored-header">
        <div>
          <div className="tailored-kicker">
            AI CAREER TOOLS
          </div>

          <h1>
            Tailored CV
          </h1>

          <p>
            Adapt your CV to a specific job,
            identify the most important gaps,
            and generate a stronger version
            for that opportunity.
          </p>
        </div>

        {result && (
          <div
            className={`match-score-box ${getScoreClass(
              matchScore
            )}`}
          >
            <span>
              Job Match
            </span>

            <strong>
              {matchScore}%
            </strong>

            <small>
              {matchLabel}
            </small>
          </div>
        )}
      </div>

      {/* =====================================================
          MESSAGES
          ===================================================== */}

      {error && (
        <div
          className="tailored-error"
          role="alert"
        >
          <span>!</span>

          <div>
            <strong>
              Something went wrong
            </strong>

            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={() =>
              setError("")
            }
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div
          className="tailored-success"
          role="status"
        >
          <span>✓</span>

          <p>
            {successMessage}
          </p>

          <button
            type="button"
            onClick={() =>
              setSuccessMessage("")
            }
            aria-label="Close success message"
          >
            ×
          </button>
        </div>
      )}

      {/* =====================================================
          SETUP FORM
          ===================================================== */}

      <div className="tailored-form-card">
        <div className="tailored-form-heading">
          <div>
            <span className="result-kicker">
              JOB TARGETING
            </span>

            <h2>
              Tailor your CV for a specific role
            </h2>

            <p>
              Give the AI the job context and
              your source CV. It will identify
              skills, gaps, and relevant projects.
            </p>
          </div>

          {result && (
            <button
              type="button"
              className="secondary-button"
              onClick={handleReset}
            >
              New Analysis
            </button>
          )}
        </div>

        <form
          onSubmit={handleAnalyze}
        >
          <div className="form-grid">
            {/* JOB TITLE */}

            <div className="form-field">
              <label htmlFor="job-title">
                Job Title
              </label>

              <input
                id="job-title"
                type="text"
                value={jobTitle}
                onChange={(event) =>
                  setJobTitle(
                    event.target.value
                  )
                }
                placeholder="e.g. Full Stack Developer"
                maxLength={150}
                disabled={analyzing}
              />

              <small>
                Enter the exact role you're
                targeting.
              </small>
            </div>

            {/* SOURCE CV */}

            <div className="form-field">
              <label htmlFor="source-cv">
                Source CV
              </label>

              {cvs.length > 0 ? (
                <>
                  <select
                    id="source-cv"
                    value={selectedCV}
                    onChange={(event) =>
                      setSelectedCV(
                        event.target.value
                      )
                    }
                    disabled={analyzing}
                  >
                    <option value="">
                      Select a CV
                    </option>

                    {cvs.map((cv) => (
                      <option
                        key={cv.id}
                        value={cv.id}
                      >
                        {cv.title ||
                          "My CV"}
                      </option>
                    ))}
                  </select>

                  {selectedCVObject && (
                    <small>
                      Using:{" "}
                      <strong>
                        {
                          selectedCVObject.title
                        }
                      </strong>
                    </small>
                  )}
                </>
              ) : (
                <div className="no-cv-message">
                  Upload a CV first.
                </div>
              )}
            </div>
          </div>

          {/* JOB DESCRIPTION */}

          <div className="form-field">
            <div className="field-heading">
              <label htmlFor="job-description">
                Job Description
              </label>

              <span>
                {jobDescriptionLength}
                {" "}characters
              </span>
            </div>

            <textarea
              id="job-description"
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(
                  event.target.value
                )
              }
              rows={9}
              placeholder="Paste the complete job description here..."
              disabled={analyzing}
            />

            <div className="field-meta">
              <small>
                {jobDescriptionWords} words
              </small>

              <small>
                A complete description produces
                a more accurate analysis.
              </small>
            </div>
          </div>

          {/* REQUIRED SKILLS */}

          <div className="form-field">
            <div className="field-heading">
              <label htmlFor="required-skills">
                Required Skills
              </label>

              <span>
                {requiredSkillList.length}
                {" "}skills
              </span>
            </div>

            <input
              id="required-skills"
              type="text"
              value={requiredSkills}
              onChange={(event) =>
                setRequiredSkills(
                  event.target.value
                )
              }
              placeholder="Python, Django, React, PostgreSQL, Docker"
              disabled={analyzing}
            />

            <small>
              Separate skills with commas.
              You can also leave this field
              empty and rely on the job
              description.
            </small>

            {requiredSkillList.length >
              0 && (
              <div className="input-skills-preview">
                {requiredSkillList.map(
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
          </div>

          {/* SUBMIT */}

          <button
            type="submit"
            className="analyze-job-button"
            disabled={!formReady}
          >
            {analyzing ? (
              <>
                <span className="button-spinner" />
                Analyzing Job...
              </>
            ) : (
              <>
                Analyze & Tailor CV
                <span>→</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* =====================================================
          RESULTS
          ===================================================== */}

      {result && (
        <div className="tailored-results">
          {/* =================================================
              MATCH OVERVIEW
          ================================================= */}

          <section className="result-card match-analysis-card">
            <div className="result-card-header">
              <div>
                <span className="result-kicker">
                  MATCH ANALYSIS
                </span>

                <h2>
                  Your Job Fit
                </h2>

                <p>
                  Here's how your current
                  profile aligns with this
                  opportunity.
                </p>
              </div>

              <div className="result-summary-score">
                <span>
                  Overall Match
                </span>

                <strong>
                  {matchScore}%
                </strong>
              </div>
            </div>

            <div className="fit-overview">
              <div
                className={`fit-score-ring ${getScoreClass(
                  matchScore
                )}`}
                style={{
                  "--fit-score": `${Math.min(
                    matchScore,
                    100
                  )}%`,
                }}
              >
                <div>
                  <strong>
                    {matchScore}%
                  </strong>

                  <span>
                    Match
                  </span>
                </div>
              </div>

              <div className="fit-overview-content">
                <span className="fit-label">
                  {matchLabel}
                </span>

                <h3>
                  {result?.job?.title ||
                    jobTitle}
                </h3>

                <p>
                  {matchDescription}
                </p>

                <div className="fit-mini-progress">
                  <span
                    style={{
                      width: `${Math.min(
                        matchScore,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="skill-match-banner">
              <div>
                <span>
                  Skill Match
                </span>

                <strong>
                  {skillMatchScore}%
                </strong>
              </div>

              <div className="banner-progress">
                <span
                  style={{
                    width: `${Math.min(
                      skillMatchScore,
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>

            {/* SKILL GROUPS */}

            <div className="skill-groups">
              {/* MATCHED */}

              <div className="skill-group matched-group">
                <div className="skill-group-header">
                  <div>
                    <span className="group-kicker">
                      STRENGTHS
                    </span>

                    <h3>
                      Matched Skills
                    </h3>
                  </div>

                  <span className="group-count">
                    {matchedSkills.length}
                  </span>
                </div>

                <div className="skill-list">
                  {matchedSkills.length >
                  0 ? (
                    matchedSkills.map(
                      (skill) => (
                        <span
                          className="skill matched"
                          key={skill}
                        >
                          <span>
                            ✓
                          </span>
                          {skill}
                        </span>
                      )
                    )
                  ) : (
                    <span className="empty-result">
                      No direct matches
                      found.
                    </span>
                  )}
                </div>
              </div>

              {/* MISSING */}

              <div className="skill-group missing-group">
                <div className="skill-group-header">
                  <div>
                    <span className="group-kicker">
                      DEVELOPMENT AREAS
                    </span>

                    <h3>
                      Skill Gaps
                    </h3>
                  </div>

                  <span className="group-count">
                    {missingSkills.length}
                  </span>
                </div>

                <div className="skill-list">
                  {missingSkills.length >
                  0 ? (
                    missingSkills.map(
                      (skill) => (
                        <span
                          className="skill missing"
                          key={skill}
                        >
                          <span>
                            +
                          </span>
                          {skill}
                        </span>
                      )
                    )
                  ) : (
                    <span className="empty-result">
                      No major skill
                      gaps detected.
                    </span>
                  )}
                </div>
              </div>
            </div>
          </section>

          {/* =================================================
              TAILORED SUMMARY
          ================================================= */}

          <section className="result-card">
            <div className="result-card-header">
              <div>
                <span className="result-kicker">
                  CV CONTENT
                </span>

                <h2>
                  Tailored Professional Summary
                </h2>

                <p>
                  A summary optimized for
                  the target role.
                </p>
              </div>
            </div>

            <div className="summary-preview">
              <div className="summary-quote">
                “
              </div>

              <p>
                {result.tailored_summary ||
                  "No tailored summary was generated."}
              </p>
            </div>
          </section>

          {/* =================================================
              RECOMMENDED PROJECTS
          ================================================= */}

          <section className="result-card">
            <div className="result-card-header">
              <div>
                <span className="result-kicker">
                  PROJECT SELECTION
                </span>

                <h2>
                  Projects You Should Highlight
                </h2>

                <p>
                  The most relevant completed
                  projects for this role.
                </p>
              </div>

              <span className="projects-result-count">
                {recommendedProjects.length}
                {" "}recommended
              </span>
            </div>

            {recommendedProjects.length >
            0 ? (
              <div className="recommended-projects">
                {recommendedProjects.map(
                  (project, index) => (
                    <article
                      className="recommended-project"
                      key={project.id}
                    >
                      <div className="project-ranking">
                        #{index + 1}
                      </div>

                      <div className="project-content">
                        <div className="project-top">
                          <div>
                            <h3>
                              {
                                project.title
                              }
                            </h3>

                            {project.target_role && (
                              <span>
                                {
                                  project.target_role
                                }
                              </span>
                            )}
                          </div>

                          <div className="project-relevance">
                            <strong>
                              {
                                project.relevance_score
                              }
                              %
                            </strong>

                            <span>
                              relevance
                            </span>
                          </div>
                        </div>

                        {project.description && (
                          <p>
                            {
                              project.description
                            }
                          </p>
                        )}

                        {Array.isArray(
                          project.skills
                        ) &&
                          project.skills
                            .length >
                            0 && (
                            <div className="project-skills">
                              {project.skills.map(
                                (
                                  skill
                                ) => (
                                  <span
                                    key={`${project.id}-${skill}`}
                                  >
                                    {
                                      skill
                                    }
                                  </span>
                                )
                              )}
                            </div>
                          )}

                        <div className="project-links">
                          {project.github_url && (
                            <a
                              href={
                                project.github_url
                              }
                              target="_blank"
                              rel="noreferrer"
                            >
                              GitHub
                              <span>
                                ↗
                              </span>
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
                              Live Demo
                              <span>
                                ↗
                              </span>
                            </a>
                          )}

                          {!project.github_url &&
                            !project.demo_url && (
                              <span className="no-project-link">
                                No portfolio links
                                added yet.
                              </span>
                            )}
                        </div>
                      </div>
                    </article>
                  )
                )}
              </div>
            ) : (
              <div className="empty-result large">
                <strong>
                  No completed projects found.
                </strong>

                <p>
                  Complete projects from
                  My Projects to make your
                  tailored CV stronger.
                </p>
              </div>
            )}
          </section>

          {/* =================================================
              FINAL ACTION
          ================================================= */}

          <section className="tailored-generate-card">
            <div className="generate-icon">
              CV
            </div>

            <div className="generate-content">
              <span className="result-kicker">
                FINAL STEP
              </span>

              <h2>
                Your Tailored CV is Ready
              </h2>

              <p>
                Your source CV, matched
                skills, tailored summary,
                and recommended projects
                are ready to be combined
                into a job-specific PDF.
              </p>

              <div className="generate-checks">
                <span>
                  ✓ Tailored summary
                </span>

                <span>
                  ✓ Matched skills
                </span>

                <span>
                  ✓ Relevant projects
                </span>
              </div>
            </div>

            <button
              type="button"
              className="generate-tailored-button"
              onClick={
                handleGenerateTailoredPDF
              }
              disabled={generatingPDF}
            >
              {generatingPDF ? (
                <>
                  <span className="button-spinner" />
                  Generating PDF...
                </>
              ) : (
                <>
                  Generate Tailored CV PDF
                  <span>↓</span>
                </>
              )}
            </button>
          </section>
        </div>
      )}
    </div>
  );
}

export default TailoredCV;