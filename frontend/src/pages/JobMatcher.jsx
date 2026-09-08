import { useEffect, useMemo, useState } from "react";

import {
  getMyCVs,
  matchJob,
  createSkillGap,
  analyzeCareerJobMatch,
} from "../services/api";

import "./JobMatcher.css";

function JobMatcher() {
  const [cvs, setCVs] = useState([]);
  const [selectedCV, setSelectedCV] = useState("");

  const [jobDescription, setJobDescription] =
    useState("");

  const [result, setResult] = useState(null);

  /*
   * Legacy job-matching result.
   * Kept for backwards compatibility with the
   * existing /api/job-matching/ endpoint.
   */
  const [legacyResult, setLegacyResult] =
    useState(null);

  const [skillGap, setSkillGap] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [loadingGap, setLoadingGap] =
    useState(false);

  const [error, setError] =
    useState("");

  const [copied, setCopied] =
    useState(false);

  /* =========================================================
     LOAD CVs
  ========================================================= */

  useEffect(() => {
    let mounted = true;

    const loadCVs = async () => {
      try {
        setError("");

        const data = await getMyCVs();

        if (!mounted) {
          return;
        }

        const safeCVs =
          Array.isArray(data)
            ? data
            : Array.isArray(data?.results)
            ? data.results
            : [];

        setCVs(safeCVs);

        if (
          safeCVs.length > 0
        ) {
          setSelectedCV(
            String(
              safeCVs[0].id
            )
          );
        }
      } catch (err) {
        if (!mounted) {
          return;
        }

        setError(
          err?.message ||
            "Failed to load your CVs."
        );
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadCVs();

    return () => {
      mounted = false;
    };
  }, []);

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

  /*
   * New Career Intelligence result
   */
  const careerIntelligence =
    result?.analysis || null;

  const jobMatch =
    careerIntelligence?.job_match ||
    null;

  const skillMatch =
    jobMatch?.skill_match ||
    null;

  const applicationReadiness =
    careerIntelligence?.application_readiness ||
    null;

  const candidateProfile =
    careerIntelligence?.candidate_profile ||
    null;

  /*
   * New score
   */
  const intelligenceMatchScore =
    Number(jobMatch?.score) || 0;

  /*
   * Backwards-compatible legacy scores.
   */
  const finalMatchScore =
    intelligenceMatchScore ||
    Number(
      legacyResult?.final_match_score
    ) ||
    0;

  const semanticScore =
    Number(
      legacyResult?.semantic_score
    ) || 0;

  const skillMatchScore =
    Number(
      skillMatch?.score
    ) ||
    Number(
      legacyResult?.skill_match_score
    ) ||
    0;

  const requiredSkillCoverage =
    Number(
      skillMatch?.required_skill_coverage
    ) || 0;

  /*
   * New Job Intelligence skills
   *
   * IMPORTANT:
   * The current Career Intelligence API returns:
   *
   * analysis.job_skills
   *
   * not:
   *
   * analysis.job_match.job_skills
   *
   * Keep a defensive fallback for older response shapes.
   */
  const newRequiredSkills =
    Array.isArray(
      careerIntelligence?.job_skills
    )
      ? careerIntelligence.job_skills
      : Array.isArray(
          jobMatch?.job_skills
        )
      ? jobMatch.job_skills
      : [];

  const newMatchedSkills =
    Array.isArray(
      skillMatch?.matched
    )
      ? skillMatch.matched
      : [];

  const partialSkills =
    Array.isArray(
      skillMatch?.partial
    )
      ? skillMatch.partial
      : [];

  const newMissingSkills =
    Array.isArray(
      skillMatch?.missing
    )
      ? skillMatch.missing
      : [];

  const priorityMissingSkills =
    Array.isArray(
      jobMatch?.priority_missing_skills
    )
      ? jobMatch.priority_missing_skills
      : [];

  /*
   * Legacy skill arrays.
   */
  const legacyRequiredSkills =
    Array.isArray(
      legacyResult?.required_skills
    )
      ? legacyResult.required_skills
      : [];

  const legacyMatchedSkills =
    Array.isArray(
      legacyResult?.matched_skills
    )
      ? legacyResult.matched_skills
      : [];

  const legacyMissingSkills =
    Array.isArray(
      legacyResult?.missing_skills
    )
      ? legacyResult.missing_skills
      : [];

  /*
   * Display-compatible skill arrays.
   */
  const requiredSkills =
    newRequiredSkills.length > 0
      ? newRequiredSkills
      : legacyRequiredSkills;

  const matchedSkills =
    newMatchedSkills.length > 0
      ? newMatchedSkills
      : legacyMatchedSkills;

  const missingSkills =
    newMissingSkills.length > 0
      ? newMissingSkills
      : legacyMissingSkills;

  /*
   * Personalized roadmap directly from Career Intelligence.
   */
  const intelligentRoadmap =
    Array.isArray(
      careerIntelligence?.roadmap?.phases
    )
      ? careerIntelligence.roadmap.phases
      : [];

  /*
   * Existing legacy roadmap from Skill Gap.
   */
  const legacyRoadmap =
    Array.isArray(
      skillGap?.learning_roadmap
    )
      ? skillGap.learning_roadmap
      : [];

  const hasIntelligentRoadmap =
    intelligentRoadmap.length > 0;

  const roadmap =
    hasIntelligentRoadmap
      ? intelligentRoadmap
      : legacyRoadmap;

  const hasAnalysis =
    Boolean(
      result ||
      legacyResult
    );

  /*
   * Current Career Intelligence response keeps the detected role
   * inside job_match.role.
   *
   * Keep compatibility with any older job.title response too.
   */
  const detectedJobTitle =
    jobMatch?.role?.name ||
    jobMatch?.role?.title ||
    jobMatch?.job?.title ||
    legacyResult?.job_title ||
    "";

  const titleMatch =
    Number(
      jobMatch?.title_match
    ) || 0;

  const readinessScore =
    Number(
      applicationReadiness?.score
    ) || 0;

  const readinessLabel =
    applicationReadiness?.label ||
    "";

  const applicationVerdict =
    applicationReadiness
      ?.application_verdict ||
    null;

  const scoreLabel =
    finalMatchScore >= 85
      ? "Excellent Match"
      : finalMatchScore >= 70
      ? "Strong Match"
      : finalMatchScore >= 50
      ? "Moderate Match"
      : "Low Match";

  const scoreDescription =
    finalMatchScore >= 85
      ? "Your profile appears highly aligned with this opportunity."
      : finalMatchScore >= 70
      ? "You have a strong foundation for this role, with some areas worth improving."
      : finalMatchScore >= 50
      ? "You have partial alignment. Closing the main skill gaps could significantly improve your fit."
      : "There are several important gaps between your current profile and this role.";

  const matchReadiness =
    applicationVerdict?.verdict ||
    (finalMatchScore >= 85
      ? "Ready to Apply"
      : finalMatchScore >= 70
      ? "Nearly Ready"
      : finalMatchScore >= 50
      ? "Needs Improvement"
      : "Build Skills First");

  const descriptionLength =
    jobDescription.length;

  const descriptionWords =
    jobDescription.trim()
      ? jobDescription
          .trim()
          .split(/\s+/)
          .filter(Boolean).length
      : 0;

  /* =========================================================
     HELPERS
  ========================================================= */

  const getSkillName = (
    skill
  ) => {
    if (
      typeof skill === "string"
    ) {
      return skill;
    }

    return (
      skill?.name ||
      skill?.skill ||
      "Unknown Skill"
    );
  };

  const getSkillKey = (
    skill,
    index
  ) => {
    if (
      typeof skill === "string"
    ) {
      return `${skill}-${index}`;
    }

    return (
      skill?.skill_id ||
      skill?.id ||
      skill?.slug ||
      `${getSkillName(
        skill
      )}-${index}`
    );
  };

  const getPriorityLabel =
    (skill) => {
      if (
        skill?.importance ===
        "required"
      ) {
        return "Required";
      }

      if (
        skill?.importance ===
        "important"
      ) {
        return "Important";
      }

      if (
        skill?.importance ===
        "preferred"
      ) {
        return "Preferred";
      }

      return "";
    };

  /* =========================================================
     ANALYZE JOB
  ========================================================= */

  const handleAnalyze = async (e) => {
    e.preventDefault();

    setError("");
    setResult(null);
    setLegacyResult(null);
    setSkillGap(null);
    setCopied(false);

    if (!selectedCV) {
      setError(
        "Please select a CV."
      );
      return;
    }

    if (
      !jobDescription.trim()
    ) {
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
        "Please provide the complete job description for a more accurate analysis."
      );
      return;
    }

    try {
      setAnalyzing(true);

      /*
       * Primary engine:
       * Career Taxonomy + Candidate Intelligence
       */
      const intelligenceData =
        await analyzeCareerJobMatch(
          selectedCV,
          jobDescription.trim()
        );

      setResult(
        intelligenceData
      );

      /*
       * We intentionally do not automatically call
       * the legacy job-matching endpoint.
       *
       * This prevents duplicate analysis/API cost.
       *
       * The old endpoint remains available through
       * matchJob() for backward compatibility.
       */
      setLegacyResult(null);
    } catch (intelligenceError) {
      /*
       * Fallback to the existing job-matching endpoint.
       * This protects the current app if the new
       * Career Intelligence API is temporarily unavailable.
       */
      try {
        const legacyData =
          await matchJob(
            selectedCV,
            jobDescription.trim()
          );

        setLegacyResult(
          legacyData
        );

        setError(
          "Career Intelligence is temporarily unavailable. Showing the existing job analysis."
        );
      } catch (legacyError) {
        setError(
          intelligenceError?.message ||
            legacyError?.message ||
            "Failed to analyze this job."
        );
      }
    } finally {
      setAnalyzing(false);
    }
  };

  /* =========================================================
     GENERATE LEGACY ROADMAP
  ========================================================= */

  const handleGenerateRoadmap = async () => {
    /*
     * The new Career Intelligence endpoint already returns
     * a personalized roadmap.
     *
     * Only call the old Skill Gap endpoint when the old
     * analysis is being used.
     */

    if (
      hasIntelligentRoadmap
    ) {
      return;
    }

    if (
      !legacyResult?.id
    ) {
      setError(
        "No existing job analysis ID is available."
      );
      return;
    }

    try {
      setLoadingGap(true);
      setError("");

      const data =
        await createSkillGap(
          legacyResult.id
        );

      setSkillGap(data);
    } catch (err) {
      setError(
        err?.message ||
          "Failed to generate your learning roadmap."
      );
    } finally {
      setLoadingGap(false);
    }
  };

  /* =========================================================
     RESET
  ========================================================= */

  const handleReset = () => {
    setResult(null);
    setLegacyResult(null);
    setSkillGap(null);
    setError("");
    setCopied(false);
  };

  /* =========================================================
     COPY SUMMARY
  ========================================================= */

  const handleCopySummary =
    async () => {
      if (
        !hasAnalysis
      ) {
        return;
      }

      const matchedText =
        matchedSkills
          .map(
            getSkillName
          )
          .join(", ");

      const missingText =
        missingSkills
          .map(
            getSkillName
          )
          .join(", ");

      const priorityText =
        priorityMissingSkills
          .map(
            getSkillName
          )
          .join(", ");

      const summary = [
        `AI Job Match: ${finalMatchScore}%`,
        `Required Skill Coverage: ${requiredSkillCoverage}%`,
        `Matched Skills: ${
          matchedText ||
          "None detected"
        }`,
        `Missing Skills: ${
          missingText ||
          "None detected"
        }`,
        `Priority Skills: ${
          priorityText ||
          missingText ||
          "None detected"
        }`,
        `Application Readiness: ${
          readinessScore
            ? `${readinessScore}%`
            : matchReadiness
        }`,
        `Verdict: ${matchReadiness}`,
      ].join("\n");

      try {
        await navigator.clipboard.writeText(
          summary
        );

        setCopied(true);

        setTimeout(() => {
          setCopied(false);
        }, 2000);
      } catch {
        setError(
          "Unable to copy the analysis summary."
        );
      }
    };

  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {
    return (
      <div className="job-page">
        <div className="page-loading">
          <div className="loading-spinner" />

          <p>
            Loading your CVs...
          </p>
        </div>
      </div>
    );
  }

  /* =========================================================
     MAIN
  ========================================================= */

  return (
    <div className="job-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="page-header">
        <div>
          <span className="page-kicker">
            AI CAREER TOOL
          </span>

          <h2>
            AI Job Matcher
          </h2>

          <p>
            Compare your CV against a
            real job opportunity and
            discover exactly what you
            need to improve.
          </p>
        </div>

        {hasAnalysis && (
          <button
            type="button"
            className="secondary-button"
            onClick={
              handleReset
            }
          >
            New Analysis
          </button>
        )}
      </div>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="error-message">
          <div>
            <strong>
              Something went wrong
            </strong>

            <span>
              {error}
            </span>
          </div>

          <button
            type="button"
            className="error-close"
            onClick={() =>
              setError("")
            }
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      {/* =====================================================
          QUICK EXPLANATION
      ===================================================== */}

      {!hasAnalysis &&
        cvs.length > 0 && (
          <div className="matcher-intro-grid">

            <div className="matcher-intro-card">
              <span className="intro-icon">
                CV
              </span>

              <div>
                <strong>
                  Analyze Your Profile
                </strong>

                <p>
                  The AI builds a normalized
                  candidate profile from your
                  selected CV.
                </p>
              </div>
            </div>

            <div className="matcher-intro-card">
              <span className="intro-icon">
                AI
              </span>

              <div>
                <strong>
                  Understand Job Requirements
                </strong>

                <p>
                  Required, important,
                  and preferred skills are
                  extracted from the job.
                </p>
              </div>
            </div>

            <div className="matcher-intro-card">
              <span className="intro-icon">
                ↗
              </span>

              <div>
                <strong>
                  Know Whether to Apply
                </strong>

                <p>
                  Get your match score,
                  missing skills, and
                  personalized next steps.
                </p>
              </div>
            </div>

          </div>
        )}

      {/* =====================================================
          JOB FORM
      ===================================================== */}

      <section className="job-form-card">

        <div className="section-heading">
          <div>
            <span className="section-kicker">
              JOB ANALYSIS
            </span>

            <h3>
              Analyze a Job
            </h3>

            <p>
              Select your CV and paste
              the complete job description
              to get your personalized
              match analysis.
            </p>
          </div>

          <div className="analysis-status">
            {hasAnalysis
              ? "Analysis Complete"
              : "Ready to Analyze"}
          </div>
        </div>

        <form
          className="job-form"
          onSubmit={
            handleAnalyze
          }
        >

          {/* CV */}

          <div className="form-group">

            <label htmlFor="job-cv">
              Select CV
            </label>

            <select
              id="job-cv"
              value={selectedCV}
              onChange={(e) => {
                setSelectedCV(
                  e.target.value
                );

                setResult(
                  null
                );

                setLegacyResult(
                  null
                );

                setSkillGap(
                  null
                );
              }}
              disabled={analyzing}
            >
              <option value="">
                Select a CV
              </option>

              {cvs.map(
                (cv) => (
                  <option
                    key={cv.id}
                    value={cv.id}
                  >
                    {cv.title}
                  </option>
                )
              )}
            </select>

            {selectedCVObject && (
              <small className="field-hint">
                Using{" "}
                <strong>
                  {
                    selectedCVObject.title
                  }
                </strong>
              </small>
            )}
          </div>

          {/* Job Description */}

          <div className="form-group">

            <div className="field-label-row">
              <label htmlFor="job-description">
                Job Description
              </label>

              <span className="character-count">
                {
                  descriptionLength
                }{" "}
                characters
              </span>
            </div>

            <textarea
              id="job-description"
              value={
                jobDescription
              }
              onChange={(e) =>
                setJobDescription(
                  e.target.value
                )
              }
              placeholder={
                "Paste the complete job description here..."
              }
              rows={12}
              disabled={
                analyzing
              }
            />

            <div className="textarea-meta">
              <span>
                {
                  descriptionWords
                }{" "}
                words
              </span>

              <span>
                Include responsibilities,
                requirements, and preferred
                skills for better results.
              </span>
            </div>
          </div>

          {/* ACTION */}

          <button
            type="submit"
            className="primary-button"
            disabled={
              analyzing ||
              cvs.length === 0 ||
              !selectedCV ||
              !jobDescription.trim()
            }
          >
            {analyzing ? (
              <>
                <span className="button-spinner" />
                Analyzing Job...
              </>
            ) : (
              <>
                Analyze Job
                <span>
                  →
                </span>
              </>
            )}
          </button>

        </form>

        {/* No CV */}

        {cvs.length === 0 && (
          <div className="empty-state">

            <div className="empty-state-icon">
              📄
            </div>

            <h3>
              No CV Available
            </h3>

            <p>
              Upload a CV first to use
              the Job Matcher.
            </p>

          </div>
        )}

      </section>

      {/* =====================================================
          RESULTS
      ===================================================== */}

      {hasAnalysis && (
        <section className="results-card">

          {/* RESULT HEADER */}

          <div className="results-header">

            <div className="section-heading">
              <div>

                <span className="section-kicker">
                  AI ANALYSIS
                </span>

                <h3>
                  Match Results
                </h3>

                <p>
                  Here's how your CV
                  compares with this job.
                </p>

              </div>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={
                handleCopySummary
              }
            >
              {copied
                ? "Copied ✓"
                : "Copy Summary"}
            </button>

          </div>

          {/* =================================================
              DETECTED JOB
          ================================================= */}

          {detectedJobTitle && (
            <div
              className="job-detected-banner"
              style={{
                marginBottom:
                  "20px",
                padding:
                  "16px 18px",
                borderRadius:
                  "12px",
                background:
                  "#f8fafc",
                border:
                  "1px solid #e4e7ec",
              }}
            >
              <span
                style={{
                  display:
                    "block",
                  fontSize:
                    "12px",
                  fontWeight:
                    700,
                  marginBottom:
                    "5px",
                  textTransform:
                    "uppercase",
                  letterSpacing:
                    "0.06em",
                  opacity: 0.7,
                }}
              >
                Detected Position
              </span>

              <strong>
                {detectedJobTitle}
              </strong>

              {titleMatch >
                0 && (
                <span
                  style={{
                    marginLeft:
                      "12px",
                    fontSize:
                      "13px",
                    opacity: 0.7,
                  }}
                >
                  Title alignment:{" "}
                  {
                    titleMatch
                  }
                  %
                </span>
              )}
            </div>
          )}

          {/* =================================================
              MAIN SCORE
          ================================================= */}

          <div className="match-overview">

            <div className="main-score">

              <div
                className="score-ring"
                style={{
                  "--score": `${Math.min(
                    finalMatchScore,
                    100
                  )}%`,
                }}
              >
                <div className="score-ring-inner">
                  <strong>
                    {
                      finalMatchScore
                    }%
                  </strong>

                  <span>
                    Match
                  </span>
                </div>
              </div>

              <div className="main-score-content">

                <span>
                  Final Match Score
                </span>

                <h3>
                  {
                    scoreLabel
                  }
                </h3>

                <p>
                  {
                    scoreDescription
                  }
                </p>

                <div className="readiness-badge">
                  {
                    matchReadiness
                  }
                </div>

              </div>

            </div>

            {/* SCORE CARDS */}

            <div className="score-grid">

              <div className="score-card">

                <div className="score-card-header">

                  <span>
                    Skill Match
                  </span>

                  <span className="score-card-icon">
                    ✓
                  </span>

                </div>

                <strong>
                  {
                    skillMatchScore
                  }%
                </strong>

                <div className="mini-progress">
                  <span
                    style={{
                      width: `${Math.min(
                        skillMatchScore,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <small>
                  Canonical skill alignment
                  between your profile and
                  this job.
                </small>

              </div>

              <div className="score-card">

                <div className="score-card-header">

                  <span>
                    Required Coverage
                  </span>

                  <span className="score-card-icon">
                    R
                  </span>

                </div>

                <strong>
                  {
                    requiredSkillCoverage
                  }%
                </strong>

                <div className="mini-progress">
                  <span
                    style={{
                      width: `${Math.min(
                        requiredSkillCoverage,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <small>
                  Coverage of explicitly
                  required job skills.
                </small>

              </div>

              {semanticScore >
                0 && (
                <div className="score-card">

                  <div className="score-card-header">

                    <span>
                      Semantic Match
                    </span>

                    <span className="score-card-icon">
                      AI
                    </span>

                  </div>

                  <strong>
                    {
                      semanticScore
                    }%
                  </strong>

                  <div className="mini-progress">
                    <span
                      style={{
                        width: `${Math.min(
                          semanticScore,
                          100
                        )}%`,
                      }}
                    />
                  </div>

                  <small>
                    Score from the existing
                    semantic-matching engine.
                  </small>

                </div>
              )}

            </div>
          </div>

          {/* =================================================
              APPLICATION VERDICT
          ================================================= */}

          <div
            className="application-verdict"
            style={{
              marginTop:
                "24px",
              padding:
                "22px",
              borderRadius:
                "16px",
              border:
                applicationVerdict?.can_apply
                  ? "1px solid #abefc6"
                  : "1px solid #fed7aa",
              background:
                applicationVerdict?.can_apply
                  ? "#ecfdf3"
                  : "#fffaeb",
            }}
          >
            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "space-between",
                alignItems:
                  "center",
                gap:
                  "20px",
                flexWrap:
                  "wrap",
              }}
            >
              <div>
                <span
                  style={{
                    display:
                      "block",
                    fontSize:
                      "12px",
                    fontWeight:
                      700,
                    textTransform:
                      "uppercase",
                    letterSpacing:
                      "0.06em",
                    marginBottom:
                      "6px",
                    opacity:
                      0.65,
                  }}
                >
                  Can I Apply?
                </span>

                <strong
                  style={{
                    fontSize:
                      "22px",
                  }}
                >
                  {
                    applicationVerdict?.verdict ||
                    matchReadiness
                  }
                </strong>

                <p
                  style={{
                    margin:
                      "6px 0 0",
                    opacity:
                      0.8,
                  }}
                >
                  {
                    applicationVerdict?.reason ||
                    scoreDescription
                  }
                </p>
              </div>

              {applicationReadiness && (
                <div
                  style={{
                    textAlign:
                      "right",
                  }}
                >
                  <span
                    style={{
                      display:
                        "block",
                      opacity:
                        0.65,
                      fontSize:
                        "13px",
                    }}
                  >
                    Application Readiness
                  </span>

                  <strong
                    style={{
                      fontSize:
                        "30px",
                    }}
                  >
                    {
                      readinessScore
                    }%
                  </strong>

                  <span
                    style={{
                      display:
                        "block",
                      fontSize:
                        "13px",
                    }}
                  >
                    {
                      readinessLabel
                    }
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* =================================================
              SKILL SUMMARY
          ================================================= */}

          <div className="skill-summary-grid">

            <div className="skill-summary-card">
              <span>
                Detected
              </span>

              <strong>
                {
                  requiredSkills.length
                }
              </strong>

              <small>
                job skills
              </small>
            </div>

            <div className="skill-summary-card positive">
              <span>
                Matched
              </span>

              <strong>
                {
                  matchedSkills.length
                }
              </strong>

              <small>
                skills you already have
              </small>
            </div>

            <div className="skill-summary-card warning">
              <span>
                To Improve
              </span>

              <strong>
                {
                  partialSkills.length
                }
              </strong>

              <small>
                partially supported
                skills
              </small>
            </div>

            <div className="skill-summary-card warning">
              <span>
                Missing
              </span>

              <strong>
                {
                  missingSkills.length
                }
              </strong>

              <small>
                skills to develop
              </small>
            </div>

          </div>

          {/* =================================================
              REQUIRED / DETECTED SKILLS
          ================================================= */}

          <div className="skills-section">

            <div className="skills-section-header">

              <div>

                <span className="section-kicker">
                  REQUIREMENTS
                </span>

                <h3>
                  Job Skills
                </h3>

              </div>

              <span className="skills-count">
                {
                  requiredSkills.length
                }
              </span>

            </div>

            {requiredSkills.length >
            0 ? (
              <div className="skill-list">

                {requiredSkills.map(
                  (
                    skill,
                    index
                  ) => (
                    <span
                      className="skill-pill"
                      key={getSkillKey(
                        skill,
                        index
                      )}
                    >
                      {
                        getSkillName(
                          skill
                        )
                      }

                      {getPriorityLabel(
                        skill
                      ) && (
                        <small
                          style={{
                            marginLeft:
                              "7px",
                            opacity:
                              0.65,
                          }}
                        >
                          {getPriorityLabel(
                            skill
                          )}
                        </small>
                      )}
                    </span>
                  )
                )}

              </div>
            ) : (
              <div className="section-empty">
                <p>
                  No specific skills were
                  detected from this job
                  description.
                </p>
              </div>
            )}

          </div>

          {/* =================================================
              MATCHED SKILLS
          ================================================= */}

          <div className="skills-section matched-skills-section">

            <div className="skills-section-header">

              <div>

                <span className="section-kicker positive-text">
                  YOUR STRENGTHS
                </span>

                <h3>
                  Matched Skills
                </h3>

              </div>

              <span className="skills-count positive-count">
                {
                  matchedSkills.length
                }
              </span>

            </div>

            {matchedSkills.length >
            0 ? (
              <div className="result-list">

                {matchedSkills.map(
                  (
                    skill,
                    index
                  ) => (
                    <div
                      className="matched-item"
                      key={getSkillKey(
                        skill,
                        index
                      )}
                    >
                      <span className="result-icon">
                        ✓
                      </span>

                      <span>
                        {
                          getSkillName(
                            skill
                          )
                        }
                      </span>
                    </div>
                  )
                )}

              </div>
            ) : (
              <div className="section-empty">
                <p>
                  No matched skills were
                  detected.
                </p>
              </div>
            )}

          </div>

          {/* =================================================
              PARTIAL SKILLS
          ================================================= */}

          {partialSkills.length >
            0 && (
            <div className="skills-section">

              <div className="skills-section-header">

                <div>

                  <span className="section-kicker warning-text">
                    DEVELOPMENT AREAS
                  </span>

                  <h3>
                    Skills to Improve
                  </h3>

                </div>

                <span className="skills-count warning-count">
                  {
                    partialSkills.length
                  }
                </span>

              </div>

              <div className="result-list">

                {partialSkills.map(
                  (
                    skill,
                    index
                  ) => (
                    <div
                      className="missing-item"
                      key={getSkillKey(
                        skill,
                        index
                      )}
                    >
                      <span className="result-icon">
                        !
                      </span>

                      <div>
                        <span>
                          {
                            getSkillName(
                              skill
                            )
                          }
                        </span>

                        {typeof skill?.candidate_confidence ===
                          "number" && (
                          <small
                            style={{
                              display:
                                "block",
                              marginTop:
                                "4px",
                              opacity:
                                0.65,
                            }}
                          >
                            Evidence confidence:{" "}
                            {Math.round(
                              skill.candidate_confidence *
                                100
                            )}
                            %
                          </small>
                        )}
                      </div>
                    </div>
                  )
                )}

              </div>
            </div>
          )}

          {/* =================================================
              MISSING SKILLS
          ================================================= */}

          <div className="skills-section missing-skills-section">

            <div className="skills-section-header">

              <div>

                <span className="section-kicker warning-text">
                  DEVELOPMENT AREAS
                </span>

                <h3>
                  Missing Skills
                </h3>

              </div>

              <span className="skills-count warning-count">
                {
                  missingSkills.length
                }
              </span>

            </div>

            {missingSkills.length >
            0 ? (
              <div className="result-list">

                {missingSkills.map(
                  (
                    skill,
                    index
                  ) => (
                    <div
                      className="missing-item"
                      key={getSkillKey(
                        skill,
                        index
                      )}
                    >
                      <span className="result-icon">
                        !
                      </span>

                      <div>
                        <span>
                          {
                            getSkillName(
                              skill
                            )
                          }
                        </span>

                        {getPriorityLabel(
                          skill
                        ) && (
                          <small
                            style={{
                              display:
                                "block",
                              marginTop:
                                "4px",
                              opacity:
                                0.65,
                            }}
                          >
                            {
                              getPriorityLabel(
                                skill
                              )
                            }
                          </small>
                        )}
                      </div>
                    </div>
                  )
                )}

              </div>
            ) : (
              <div className="no-gaps-message">

                <span>
                  ✓
                </span>

                <p>
                  Great! No major missing
                  skills were detected.
                </p>

              </div>
            )}

          </div>

          {/* =================================================
              PRIORITY SKILLS
          ================================================= */}

          {priorityMissingSkills.length >
            0 && (
            <div
              className="skills-section"
              style={{
                border:
                  "1px solid #e9d7fe",
                background:
                  "#fcfaff",
              }}
            >

              <div className="skills-section-header">

                <div>

                  <span className="section-kicker">
                    PRIORITY
                  </span>

                  <h3>
                    Skills to Close First
                  </h3>

                  <p
                    style={{
                      margin:
                        "6px 0 0",
                      opacity:
                        0.7,
                    }}
                  >
                    Focus here first because
                    these gaps have the biggest
                    impact on this application.
                  </p>

                </div>

                <span className="skills-count">
                  {
                    priorityMissingSkills.length
                  }
                </span>

              </div>

              <div className="result-list">

                {priorityMissingSkills.map(
                  (
                    skill,
                    index
                  ) => (
                    <div
                      className="missing-item"
                      key={getSkillKey(
                        skill,
                        index
                      )}
                    >
                      <span className="result-icon">
                        {index + 1}
                      </span>

                      <div>

                        <strong>
                          {
                            getSkillName(
                              skill
                            )
                          }
                        </strong>

                        <small
                          style={{
                            display:
                              "block",
                            marginTop:
                              "4px",
                            opacity:
                              0.65,
                          }}
                        >
                          {
                            getPriorityLabel(
                              skill
                            )
                          }
                        </small>

                      </div>

                    </div>
                  )
                )}

              </div>

            </div>
          )}

          {/* =================================================
              ROADMAP
          ================================================= */}

          <div className="roadmap-section">

            <div className="roadmap-intro">

              <div>

                <span className="section-kicker">
                  NEXT STEP
                </span>

                <h3>
                  Close Your Skill Gaps
                </h3>

                <p>
                  Your roadmap is now built
                  from the skills required
                  by this specific job.
                </p>

              </div>

              {!hasIntelligentRoadmap && (
                <button
                  className="primary-button"
                  type="button"
                  onClick={
                    handleGenerateRoadmap
                  }
                  disabled={
                    loadingGap
                  }
                >
                  {loadingGap ? (
                    <>
                      <span className="button-spinner" />
                      Generating Roadmap...
                    </>
                  ) : (
                    <>
                      Generate Learning Roadmap
                      <span>
                        →
                      </span>
                    </>
                  )}
                </button>
              )}

            </div>

            {/* =================================================
                NEW INTELLIGENT ROADMAP
            ================================================= */}

            {hasIntelligentRoadmap && (
              <div className="roadmap-result">

                <div className="roadmap-header">

                  <div>

                    <span className="section-kicker">
                      PERSONALIZED PLAN
                    </span>

                    <h3>
                      Job-Specific Learning Roadmap
                    </h3>

                    <p>
                      Designed around your
                      current skills and the
                      requirements of{" "}
                      <strong>
                        {
                          detectedJobTitle ||
                          "this position"
                        }
                      </strong>
                      .
                    </p>

                  </div>

                  <div className="gap-score-badge">
                    {Math.max(
                      0,
                      Math.round(
                        100 -
                          requiredSkillCoverage
                      )
                    )}
                    %
                    <span>
                      Estimated Gap
                    </span>
                  </div>

                </div>

                {intelligentRoadmap.map(
                  (
                    phase,
                    phaseIndex
                  ) => (
                    <div
                      className="roadmap-item"
                      key={
                        phase.phase_id ||
                        phase.phase_number ||
                        phaseIndex
                      }
                    >

                      <div className="roadmap-number">
                        {
                          phase.phase_number ||
                          phaseIndex + 1
                        }
                      </div>

                      <div className="roadmap-content">

                        <div className="roadmap-item-header">

                          <h4>
                            {
                              phase.title
                            }
                          </h4>

                          <span className="priority priority-high">
                            Phase{" "}
                            {
                              phase.phase_number ||
                              phaseIndex + 1
                            }
                          </span>

                        </div>

                        {phase.description && (
                          <p
                            style={{
                              marginBottom:
                                "14px",
                              opacity:
                                0.75,
                            }}
                          >
                            {
                              phase.description
                            }
                          </p>
                        )}

                        {Array.isArray(
                          phase.steps
                        ) &&
                          phase.steps.length >
                            0 && (
                            <ol>
                              {phase.steps.map(
                                (
                                  step
                                ) => (
                                  <li
                                    key={
                                      step.id ||
                                      step.title
                                    }
                                  >
                                    <strong>
                                      {
                                        step.title
                                      }
                                    </strong>

                                    {step.skill
                                      ?.name && (
                                      <span
                                        style={{
                                          marginLeft:
                                            "6px",
                                          opacity:
                                            0.7,
                                        }}
                                      >
                                        (
                                        {
                                          step
                                            .skill
                                            .name
                                        }
                                        )
                                      </span>
                                    )}

                                    {step.description && (
                                      <div
                                        style={{
                                          marginTop:
                                            "4px",
                                          opacity:
                                            0.7,
                                        }}
                                      >
                                        {
                                          step.description
                                        }
                                      </div>
                                    )}
                                  </li>
                                )
                              )}
                            </ol>
                          )}

                      </div>

                    </div>
                  )
                )}

                {careerIntelligence
                  ?.roadmap
                  ?.total_hours && (
                  <div
                    style={{
                      marginTop:
                        "18px",
                      padding:
                        "12px 14px",
                      borderRadius:
                        "10px",
                      background:
                        "#f8fafc",
                    }}
                  >
                    Estimated learning
                    time:{" "}
                    <strong>
                      {
                        careerIntelligence
                          .roadmap
                          .total_hours
                      }{" "}
                      hours
                    </strong>
                  </div>
                )}

              </div>
            )}

            {/* =================================================
                LEGACY ROADMAP
            ================================================= */}

            {!hasIntelligentRoadmap &&
              skillGap && (
                <div className="roadmap-result">

                  <div className="roadmap-header">

                    <div>

                      <span className="section-kicker">
                        PERSONALIZED PLAN
                      </span>

                      <h3>
                        Your Learning Roadmap
                      </h3>

                      <p>
                        Your current skill
                        gap:{" "}
                        <strong>
                          {
                            skillGap.gap_score
                          }%
                        </strong>
                      </p>

                    </div>

                    <div className="gap-score-badge">
                      {
                        skillGap.gap_score
                      }%
                      <span>
                        Skill Gap
                      </span>
                    </div>

                  </div>

                  {roadmap.length >
                  0 ? (
                    <div className="roadmap-list">

                      {roadmap.map(
                        (
                          item,
                          index
                        ) => (
                          <div
                            className="roadmap-item"
                            key={`${item.skill}-${index}`}
                          >

                            <div className="roadmap-number">
                              {
                                index + 1
                              }
                            </div>

                            <div className="roadmap-content">

                              <div className="roadmap-item-header">

                                <h4>
                                  {
                                    item.skill
                                  }
                                </h4>

                                <span
                                  className={`priority priority-${String(
                                    item.priority ||
                                      ""
                                  ).toLowerCase()}`}
                                >
                                  Priority:{" "}
                                  {
                                    item.priority
                                  }
                                </span>

                              </div>

                              {Array.isArray(
                                item.steps
                              ) &&
                                item.steps.length >
                                  0 && (
                                  <ol>
                                    {item.steps.map(
                                      (
                                        step,
                                        stepIndex
                                      ) => (
                                        <li
                                          key={`${step}-${stepIndex}`}
                                        >
                                          {
                                            step
                                          }
                                        </li>
                                      )
                                    )}
                                  </ol>
                                )}

                            </div>

                          </div>
                        )
                      )}

                    </div>
                  ) : (
                    <div className="section-empty">
                      <p>
                        No additional learning
                        roadmap is required
                        right now.
                      </p>
                    </div>
                  )}

                </div>
              )}

          </div>

          {/* =================================================
              CANDIDATE PROFILE SNAPSHOT
          ================================================= */}

          {candidateProfile && (
            <div
              style={{
                marginTop:
                  "24px",
                padding:
                  "22px",
                borderRadius:
                  "16px",
                background:
                  "#f8fafc",
                border:
                  "1px solid #e4e7ec",
              }}
            >

              <span className="section-kicker">
                CANDIDATE INTELLIGENCE
              </span>

              <h3>
                Profile Evidence Used
              </h3>

              <div
                style={{
                  display:
                    "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(150px, 1fr))",
                  gap:
                    "12px",
                  marginTop:
                    "14px",
                }}
              >

                <div>
                  <strong>
                    {
                      candidateProfile
                        .skill_count ||
                      candidateProfile
                        .skills
                        ?.length ||
                      0
                    }
                  </strong>

                  <small
                    style={{
                      display:
                        "block",
                    }}
                  >
                    normalized skills
                  </small>
                </div>

                <div>
                  <strong>
                    {
                      candidateProfile
                        .experience
                        ?.length ||
                      0
                    }
                  </strong>

                  <small
                    style={{
                      display:
                        "block",
                    }}
                  >
                    experience records
                  </small>
                </div>

                <div>
                  <strong>
                    {
                      candidateProfile
                        .projects
                        ?.length ||
                      0
                    }
                  </strong>

                  <small
                    style={{
                      display:
                        "block",
                    }}
                  >
                    projects
                  </small>
                </div>

                <div>
                  <strong>
                    {
                      candidateProfile
                        .certifications
                        ?.length ||
                      0
                    }
                  </strong>

                  <small
                    style={{
                      display:
                        "block",
                    }}
                  >
                    certifications
                  </small>
                </div>

              </div>

            </div>
          )}

        </section>
      )}
    </div>
  );
}

export default JobMatcher;