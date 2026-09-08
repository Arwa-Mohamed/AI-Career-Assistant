import { useEffect, useMemo, useRef, useState } from "react";

import {
  deleteCV,
  getCVs,
  uploadCV,
  analyzeCV,
} from "../services/api";

import "./MyCV.css";

function MyCV() {
  const [cvs, setCVs] = useState([]);

  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [analysis, setAnalysis] = useState({});
  const [analyzingId, setAnalyzingId] =
    useState(null);

  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 5 * 1024 * 1024;

  /* =========================================================
     LOAD CVs
     ========================================================= */

  const loadCVs = async () => {
    try {
      setError("");

      const data = await getCVs();

      const safeData = Array.isArray(data)
        ? data
        : [];

      setCVs(safeData);
    } catch (err) {
      setError(
        err?.message ||
          "Failed to load your CVs."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCVs();
  }, []);

  /* =========================================================
     DERIVED DATA
     ========================================================= */

  const totalCVs = cvs.length;

  const analyzedCVs = Object.keys(analysis).filter(
    (id) => analysis[id]
  ).length;

  const averageCVScore =
    analyzedCVs > 0
      ? Math.round(
          cvs
            .map((cv) => analysis[cv.id]?.score)
            .filter(
              (score) =>
                typeof score === "number" ||
                !Number.isNaN(Number(score))
            )
            .reduce(
              (sum, score) =>
                sum + Number(score),
              0
            ) / analyzedCVs
        )
      : 0;

  const totalSkills = useMemo(() => {
    const skills = new Set();

    cvs.forEach((cv) => {
      const cvSkills =
        cv?.parsed_data?.skills;

      if (Array.isArray(cvSkills)) {
        cvSkills.forEach((skill) => {
          if (skill) {
            skills.add(skill);
          }
        });
      }
    });

    return skills.size;
  }, [cvs]);

  /* =========================================================
     FILE VALIDATION
     ========================================================= */

  const validateFile = (selectedFile) => {
    if (!selectedFile) {
      return "Please select a PDF or DOCX file.";
    }

    const fileName =
      selectedFile.name.toLowerCase();

    const isValidType =
      fileName.endsWith(".pdf") ||
      fileName.endsWith(".docx");

    if (!isValidType) {
      return "Only PDF and DOCX files are supported.";
    }

    if (
      selectedFile.size >
      MAX_FILE_SIZE
    ) {
      return "File size must not exceed 5 MB.";
    }

    return "";
  };

  /* =========================================================
     FILE SELECT
     ========================================================= */

  const handleFileChange = (e) => {
    const selectedFile =
      e.target.files?.[0] || null;

    setError("");
    setMessage("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const validationError =
      validateFile(selectedFile);

    if (validationError) {
      setFile(null);
      e.target.value = "";
      setError(validationError);
      return;
    }

    setFile(selectedFile);
  };

  /* =========================================================
     UPLOAD
     ========================================================= */

  const handleUpload = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!file) {
      setError(
        "Please select a PDF or DOCX file."
      );
      return;
    }

    const validationError =
      validateFile(file);

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setUploading(true);
      setAnalyzingId(null);

      /* -----------------------------------------
         STEP 1: Upload CV
         ----------------------------------------- */

      const uploadedCV =
        await uploadCV(
          title.trim() || "My CV",
          file
        );

      setCVs((prev) => [
        uploadedCV,
        ...prev,
      ]);

      setTitle("");
      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      /* -----------------------------------------
         STEP 2: Automatically analyze new CV
         ----------------------------------------- */

      try {
        setAnalyzingId(uploadedCV.id);

        const analysisData =
          await analyzeCV(
            uploadedCV.id
          );

        setAnalysis((prev) => ({
          ...prev,
          [uploadedCV.id]:
            analysisData,
        }));

        setMessage(
          "CV uploaded and analyzed successfully."
        );
      } catch (analysisError) {
        setMessage(
          "CV uploaded successfully, but analysis failed."
        );

        setError(
          analysisError?.message ||
            "Failed to analyze the uploaded CV."
        );
      }
    } catch (err) {
      setError(
        err?.message ||
          "Failed to upload your CV."
      );
    } finally {
      setUploading(false);
      setAnalyzingId(null);
    }
  };

  /* =========================================================
     DELETE
     ========================================================= */

  const handleDelete = async (cvId) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this CV? This action cannot be undone."
      );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setMessage("");

      await deleteCV(cvId);

      setCVs((prev) =>
        prev.filter(
          (cv) => cv.id !== cvId
        )
      );

      setAnalysis((prev) => {
        const copy = { ...prev };

        delete copy[cvId];

        return copy;
      });

      setMessage(
        "CV deleted successfully."
      );
    } catch (err) {
      setError(
        err?.message ||
          "Failed to delete this CV."
      );
    }
  };

  /* =========================================================
     ANALYZE
     ========================================================= */

  const handleAnalyze = async (cvId) => {
    try {
      setError("");
      setMessage("");
      setAnalyzingId(cvId);

      const data =
        await analyzeCV(cvId);

      setAnalysis((prev) => ({
        ...prev,
        [cvId]: data,
      }));

      setMessage(
        "CV analyzed successfully."
      );
    } catch (err) {
      setError(
        err?.message ||
          "Failed to analyze this CV."
      );
    } finally {
      setAnalyzingId(null);
    }
  };

  /* =========================================================
     SCORE HELPERS
     ========================================================= */

  const getScoreClass = (score) => {
    const value = Number(score) || 0;

    if (value >= 85) {
      return "excellent";
    }

    if (value >= 70) {
      return "good";
    }

    if (value >= 50) {
      return "average";
    }

    return "needs-work";
  };

  const getScoreLabel = (score) => {
    const value = Number(score) || 0;

    if (value >= 85) {
      return "Excellent";
    }

    if (value >= 70) {
      return "Strong";
    }

    if (value >= 50) {
      return "Needs Improvement";
    }

    return "Needs Work";
  };

  /* =========================================================
     FILE NAME
     ========================================================= */

  const getFileName = (cv) => {
    if (!cv?.file) {
      return "Unknown file";
    }

    return cv.file
      .split("/")
      .pop();
  };

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <div className="cv-page">
        <div className="page-loading">
          <div className="loading-spinner" />

          <p>
            Loading your CVs...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="cv-page">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="page-header">
        <div>
          <span className="page-kicker">
            CAREER DOCUMENTS
          </span>

          <h2>
            My CV
          </h2>

          <p>
            Upload, analyze, and manage your
            resumes from one place.
          </p>
        </div>
      </div>

      {/* =====================================================
          ALERTS
          ===================================================== */}

      {message && (
        <div
          className="success-message"
          role="status"
        >
          <span>✓</span>
          {message}
        </div>
      )}

      {error && (
        <div
          className="error-message"
          role="alert"
        >
          <div>
            <strong>
              Something went wrong
            </strong>

            <span>{error}</span>
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
          OVERVIEW
          ===================================================== */}

      <div className="cv-overview-grid">
        <div className="cv-overview-card">
          <span>Total CVs</span>

          <strong>{totalCVs}</strong>

          <small>
            Uploaded resumes
          </small>
        </div>

        <div className="cv-overview-card">
          <span>Analyzed</span>

          <strong>
            {analyzedCVs}
          </strong>

          <small>
            CVs evaluated by AI
          </small>
        </div>

        <div className="cv-overview-card">
          <span>Average Score</span>

          <strong>
            {averageCVScore || "—"}
          </strong>

          <small>
            Across analyzed CVs
          </small>
        </div>

        <div className="cv-overview-card">
          <span>Detected Skills</span>

          <strong>
            {totalSkills}
          </strong>

          <small>
            Unique skills discovered
          </small>
        </div>
      </div>

      {/* =====================================================
          UPLOAD
          ===================================================== */}

      <section className="cv-upload-card">
        <div className="section-heading">
          <div>
            <span className="section-kicker">
              ADD DOCUMENT
            </span>

            <h3>
              Upload New CV
            </h3>

            <p>
              Upload your latest resume to
              analyze its content and identify
              career strengths and gaps.
            </p>
          </div>

          <div className="supported-format-badge">
            PDF / DOCX
          </div>
        </div>

        <form
          className="upload-form"
          onSubmit={handleUpload}
        >
          <div className="form-group">
            <label htmlFor="cv-title">
              CV Title
            </label>

            <input
              id="cv-title"
              type="text"
              value={title}
              onChange={(e) =>
                setTitle(
                  e.target.value
                )
              }
              placeholder="e.g. Backend Developer CV"
              maxLength={150}
              disabled={uploading}
            />

            <span className="field-hint">
              Give your CV a recognizable
              name.
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="cv-file">
              Resume File
            </label>

            <div
              className={`file-upload-box ${
                file
                  ? "has-file"
                  : ""
              }`}
            >
              <input
                ref={fileInputRef}
                id="cv-file"
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleFileChange}
                disabled={uploading}
                required
              />

              <label
                htmlFor="cv-file"
                className="file-upload-label"
              >
                <span className="file-upload-icon">
                  {file
                    ? "✓"
                    : "↑"}
                </span>

                <span className="file-upload-content">
                  <strong>
                    {file
                      ? file.name
                      : "Choose your CV"}
                  </strong>

                  <small>
                    {file
                      ? `${(
                          file.size /
                          1024 /
                          1024
                        ).toFixed(2)} MB`
                      : "PDF or DOCX • Maximum 5 MB"}
                  </small>
                </span>

                <span className="file-upload-action">
                  {file
                    ? "Change"
                    : "Browse"}
                </span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={
              uploading ||
              !file
            }
          >
            {uploading ? (
              <>
                <span className="button-spinner" />
                Uploading...
              </>
            ) : (
              <>
                Upload CV
                <span>→</span>
              </>
            )}
          </button>
        </form>
      </section>

      {/* =====================================================
          CV LIST
          ===================================================== */}

      <section className="cv-list-section">
        <div className="section-heading">
          <div>
            <span className="section-kicker">
              YOUR DOCUMENTS
            </span>

            <h3>
              Your CVs
            </h3>

            <p>
              Manage and analyze your
              uploaded resumes.
            </p>
          </div>

          {cvs.length > 0 && (
            <span className="cv-count-badge">
              {cvs.length}{" "}
              {cvs.length === 1
                ? "CV"
                : "CVs"}
            </span>
          )}
        </div>

        {cvs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              📄
            </div>

            <h3>
              No CVs Yet
            </h3>

            <p>
              Upload your first CV to start
              analyzing your career profile.
            </p>
          </div>
        ) : (
          <div className="cv-grid">
            {cvs.map((cv) => {
              const currentAnalysis =
                analysis[cv.id];

              const score =
                currentAnalysis?.score;

              const scoreClass =
                getScoreClass(score);

              return (
                <article
                  className="cv-card"
                  key={cv.id}
                >
                  {/* CARD HEADER */}

                  <div className="cv-card-header">
                    <div className="cv-title-area">
                      <div className="cv-file-icon">
                        {getFileName(
                          cv
                        )
                          .toLowerCase()
                          .endsWith(".pdf")
                          ? "PDF"
                          : "DOC"}
                      </div>

                      <div>
                        <h3>
                          {cv.title ||
                            "My CV"}
                        </h3>

                        <p
                          title={getFileName(
                            cv
                          )}
                        >
                          {getFileName(
                            cv
                          )}
                        </p>
                      </div>
                    </div>

                    <span className="cv-id">
                      #{cv.id}
                    </span>
                  </div>

                  {/* CV META */}

                  <div className="cv-meta-grid">
                    <div className="cv-meta-item">
                      <span>
                        Extracted Text
                      </span>

                      <strong>
                        {cv.extracted_text
                          ?.length ||
                          0}
                        <small>
                          {" "}chars
                        </small>
                      </strong>
                    </div>

                    <div className="cv-meta-item">
                      <span>
                        Skills
                      </span>

                      <strong>
                        {Array.isArray(
                          cv
                            .parsed_data
                            ?.skills
                        )
                          ? cv
                              .parsed_data
                              .skills
                              .length
                          : 0}
                      </strong>
                    </div>
                  </div>

                  {/* SKILLS */}

                  {Array.isArray(
                    cv.parsed_data
                      ?.skills
                  ) &&
                    cv.parsed_data
                      .skills.length >
                      0 && (
                      <div className="skills-block">
                        <div className="skills-block-header">
                          <h4>
                            Detected Skills
                          </h4>

                          <span>
                            {
                              cv.parsed_data
                                .skills
                                .length
                            }
                          </span>
                        </div>

                        <div className="skill-list">
                          {cv.parsed_data.skills.map(
                            (skill) => (
                              <span
                                className="skill-pill"
                                key={skill}
                              >
                                {skill}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}

                  {/* ACTIONS */}

                  <div className="cv-actions">
                    <button
                      className="primary-button"
                      onClick={() =>
                        handleAnalyze(
                          cv.id
                        )
                      }
                      disabled={
                        analyzingId ===
                        cv.id
                      }
                    >
                      {analyzingId ===
                      cv.id ? (
                        <>
                          <span className="button-spinner" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          Analyze CV
                          <span>
                            →
                          </span>
                        </>
                      )}
                    </button>

                    <button
                      className="secondary-button"
                      onClick={() =>
                        handleDelete(
                          cv.id
                        )
                      }
                      disabled={
                        analyzingId ===
                        cv.id ||
                        uploading
                      }
                    >
                      Delete
                    </button>
                  </div>

                  {/* ANALYSIS */}

                  {currentAnalysis && (
                    <div className="analysis-card">
                      <div className="analysis-header">
                        <div>
                          <span className="section-kicker">
                            AI ANALYSIS
                          </span>

                          <h4>
                            Resume Assessment
                          </h4>
                        </div>

                        <div
                          className={`analysis-score-badge ${scoreClass}`}
                        >
                          <span>
                            CV Score
                          </span>

                          <strong>
                            {score ?? 0}
                            <small>
                              /100
                            </small>
                          </strong>
                        </div>
                      </div>

                      <div className="analysis-status">
                        {getScoreLabel(
                          score
                        )}
                      </div>

                      {/* SCORE BREAKDOWN */}

                      {currentAnalysis
                        .breakdown && (
                        <div className="analysis-breakdown">
                          <div className="analysis-section-title">
                            <h4>
                              Score Breakdown
                            </h4>
                          </div>

                          <div className="breakdown-list">
                            <div className="breakdown-item">
                              <span>
                                Contact
                              </span>

                              <div className="breakdown-value">
                                <strong>
                                  {
                                    currentAnalysis
                                      .breakdown
                                      .contact_information
                                  }
                                </strong>

                                <div className="breakdown-progress">
                                  <span
                                    style={{
                                      width: `${Math.min(
                                        Number(
                                          currentAnalysis
                                            .breakdown
                                            .contact_information
                                        ) ||
                                          0,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="breakdown-item">
                              <span>
                                Skills
                              </span>

                              <div className="breakdown-value">
                                <strong>
                                  {
                                    currentAnalysis
                                      .breakdown
                                      .skills
                                  }
                                </strong>

                                <div className="breakdown-progress">
                                  <span
                                    style={{
                                      width: `${Math.min(
                                        Number(
                                          currentAnalysis
                                            .breakdown
                                            .skills
                                        ) || 0,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="breakdown-item">
                              <span>
                                Content
                              </span>

                              <div className="breakdown-value">
                                <strong>
                                  {
                                    currentAnalysis
                                      .breakdown
                                      .content
                                  }
                                </strong>

                                <div className="breakdown-progress">
                                  <span
                                    style={{
                                      width: `${Math.min(
                                        Number(
                                          currentAnalysis
                                            .breakdown
                                            .content
                                        ) || 0,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </div>

                            <div className="breakdown-item">
                              <span>
                                Sections
                              </span>

                              <div className="breakdown-value">
                                <strong>
                                  {
                                    currentAnalysis
                                      .breakdown
                                      .sections
                                  }
                                </strong>

                                <div className="breakdown-progress">
                                  <span
                                    style={{
                                      width: `${Math.min(
                                        Number(
                                          currentAnalysis
                                            .breakdown
                                            .sections
                                        ) || 0,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* SECTIONS */}

                      {currentAnalysis.sections && (
                        <div className="sections-result">
                          <div className="analysis-section-title">
                            <h4>
                              Resume Sections
                            </h4>
                          </div>

                          <div className="sections-grid">
                            <div
                              className={
                                currentAnalysis
                                  .sections
                                  .education
                                  ? "section-status complete"
                                  : "section-status missing"
                              }
                            >
                              <span>
                                {currentAnalysis
                                  .sections
                                  .education
                                  ? "✓"
                                  : "!"}
                              </span>

                              <div>
                                <strong>
                                  Education
                                </strong>

                                <small>
                                  {currentAnalysis
                                    .sections
                                    .education
                                    ? "Detected"
                                    : "Missing"}
                                </small>
                              </div>
                            </div>

                            <div
                              className={
                                currentAnalysis
                                  .sections
                                  .experience
                                  ? "section-status complete"
                                  : "section-status missing"
                              }
                            >
                              <span>
                                {currentAnalysis
                                  .sections
                                  .experience
                                  ? "✓"
                                  : "!"}
                              </span>

                              <div>
                                <strong>
                                  Experience
                                </strong>

                                <small>
                                  {currentAnalysis
                                    .sections
                                    .experience
                                    ? "Detected"
                                    : "Missing"}
                                </small>
                              </div>
                            </div>

                            <div
                              className={
                                currentAnalysis
                                  .sections
                                  .projects
                                  ? "section-status complete"
                                  : "section-status missing"
                              }
                            >
                              <span>
                                {currentAnalysis
                                  .sections
                                  .projects
                                  ? "✓"
                                  : "!"}
                              </span>

                              <div>
                                <strong>
                                  Projects
                                </strong>

                                <small>
                                  {currentAnalysis
                                    .sections
                                    .projects
                                    ? "Detected"
                                    : "Missing"}
                                </small>
                              </div>
                            </div>

                            <div
                              className={
                                currentAnalysis
                                  .sections
                                  .certifications
                                  ? "section-status complete"
                                  : "section-status missing"
                              }
                            >
                              <span>
                                {currentAnalysis
                                  .sections
                                  .certifications
                                  ? "✓"
                                  : "!"}
                              </span>

                              <div>
                                <strong>
                                  Certifications
                                </strong>

                                <small>
                                  {currentAnalysis
                                    .sections
                                    .certifications
                                    ? "Detected"
                                    : "Missing"}
                                </small>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* ANALYSIS FOOTER */}

                      <div className="analysis-footer">
                        <span>
                          AI analysis completed
                          successfully.
                        </span>
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default MyCV;