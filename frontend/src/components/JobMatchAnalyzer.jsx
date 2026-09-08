import { useState } from "react";

import { analyzeJobAgainstCV } from "../services/jobIntelligence";

export default function JobMatchAnalyzer({
  cvs = [],
}) {
  const [selectedCvId, setSelectedCvId] =
    useState("");

  const [jobDescription, setJobDescription] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const handleAnalyze = async () => {
    setError("");
    setResult(null);

    if (!selectedCvId) {
      setError(
        "Please select a CV first."
      );
      return;
    }

    if (
      !jobDescription.trim() ||
      jobDescription.trim().length < 30
    ) {
      setError(
        "Please enter a complete job description."
      );
      return;
    }

    try {
      setLoading(true);

      const response =
        await analyzeJobAgainstCV({
          cvId: selectedCvId,
          jobDescription,
        });

      setResult(
        response.analysis
      );
    } catch (err) {
      setError(
        err.message ||
          "Failed to analyze the job."
      );
    } finally {
      setLoading(false);
    }
  };

  const jobMatch =
    result?.job_match;

  const skillMatch =
    jobMatch?.skill_match;

  const readiness =
    result?.application_readiness;

  const getScoreClass = (score) => {
    if (score >= 80) {
      return "score score-high";
    }

    if (score >= 60) {
      return "score score-medium";
    }

    return "score score-low";
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "1000px",
        margin: "0 auto",
      }}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: "20px",
          padding: "28px",
          boxShadow:
            "0 10px 35px rgba(0,0,0,0.08)",
          border:
            "1px solid #e8edf3",
        }}
      >
        <div
          style={{
            marginBottom: "24px",
          }}
        >
          <h2
            style={{
              margin: 0,
              fontSize: "28px",
              color: "#172033",
            }}
          >
            Job Match Analyzer
          </h2>

          <p
            style={{
              marginTop: "8px",
              color: "#667085",
              lineHeight: 1.6,
            }}
          >
            Paste a job description and the AI
            will compare it against your CV,
            identify missing skills, and tell you
            whether you are ready to apply.
          </p>
        </div>

        {/* CV Selection */}

        <div
          style={{
            marginBottom: "20px",
          }}
        >
          <label
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
              color: "#344054",
            }}
          >
            Select CV
          </label>

          <select
            value={selectedCvId}
            onChange={(event) =>
              setSelectedCvId(
                event.target.value
              )
            }
            style={{
              width: "100%",
              padding: "13px 14px",
              borderRadius: "10px",
              border:
                "1px solid #d0d5dd",
              fontSize: "15px",
              background: "#ffffff",
            }}
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
                  `CV #${cv.id}`}
              </option>
            ))}
          </select>
        </div>

        {/* Job Description */}

        <div
          style={{
            marginBottom: "20px",
          }}
        >
          <label
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
              color: "#344054",
            }}
          >
            Job Description
          </label>

          <textarea
            value={jobDescription}
            onChange={(event) =>
              setJobDescription(
                event.target.value
              )
            }
            placeholder={`Paste the complete job description here...

Example:
Data Analyst
Required: SQL, Excel, Statistics
Experience with Power BI
Python is preferred
Strong communication skills...`}
            rows={12}
            style={{
              width: "100%",
              padding: "14px",
              borderRadius: "10px",
              border:
                "1px solid #d0d5dd",
              fontSize: "15px",
              lineHeight: 1.6,
              resize: "vertical",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* Error */}

        {error && (
          <div
            style={{
              marginBottom: "20px",
              padding: "14px 16px",
              borderRadius: "10px",
              background:
                "#fff1f1",
              border:
                "1px solid #f5c2c7",
              color: "#b42318",
            }}
          >
            {error}
          </div>
        )}

        {/* Analyze Button */}

        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px 18px",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            fontWeight: 700,
            cursor: loading
              ? "not-allowed"
              : "pointer",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading
            ? "Analyzing Job..."
            : "Analyze Job Match"}
        </button>
      </div>

      {/* Results */}

      {result && (
        <div
          style={{
            marginTop: "24px",
            display: "grid",
            gap: "20px",
          }}
        >
          {/* Main Score */}

          <div
            style={{
              background: "#ffffff",
              borderRadius: "20px",
              padding: "28px",
              boxShadow:
                "0 10px 35px rgba(0,0,0,0.08)",
              textAlign: "center",
            }}
          >
            <div
              style={{
                color: "#667085",
                marginBottom: "8px",
              }}
            >
              Job Match Score
            </div>

            <div
              style={{
                fontSize: "56px",
                fontWeight: 800,
                marginBottom: "10px",
              }}
            >
              {jobMatch?.score ?? 0}%
            </div>

            <div
              style={{
                fontSize: "18px",
                fontWeight: 700,
                marginBottom: "8px",
              }}
            >
              {jobMatch?.verdict?.label ||
                "Analysis Complete"}
            </div>

            <p
              style={{
                margin: 0,
                color: "#667085",
              }}
            >
              {jobMatch?.verdict
                ?.description || ""}
            </p>
          </div>

          {/* Readiness */}

          {readiness && (
            <div
              style={{
                background: "#ffffff",
                borderRadius: "20px",
                padding: "24px",
                boxShadow:
                  "0 10px 35px rgba(0,0,0,0.08)",
              }}
            >
              <h3
                style={{
                  marginTop: 0,
                  color: "#172033",
                }}
              >
                Application Readiness
              </h3>

              <div
                className={getScoreClass(
                  readiness.score
                )}
                style={{
                  fontSize: "32px",
                  fontWeight: 800,
                  marginBottom: "8px",
                }}
              >
                {readiness.score}%
              </div>

              <strong>
                {readiness.label}
              </strong>

              <p
                style={{
                  color: "#667085",
                  lineHeight: 1.6,
                }}
              >
                {readiness.description}
              </p>
            </div>
          )}

          {/* Skill Coverage */}

          <div
            style={{
              background: "#ffffff",
              borderRadius: "20px",
              padding: "24px",
              boxShadow:
                "0 10px 35px rgba(0,0,0,0.08)",
            }}
          >
            <h3
              style={{
                marginTop: 0,
              }}
            >
              Skill Coverage
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "14px",
              }}
            >
              <StatCard
                title="Overall"
                value={`${skillMatch?.score ?? 0}%`}
              />

              <StatCard
                title="Required Skills"
                value={`${skillMatch?.required_skill_coverage ?? 0}%`}
              />

              <StatCard
                title="Matched"
                value={
                  skillMatch?.matched
                    ?.length ?? 0
                }
              />

              <StatCard
                title="Missing"
                value={
                  skillMatch?.missing
                    ?.length ?? 0
                }
              />
            </div>
          </div>

          {/* Matched Skills */}

          <SkillSection
            title="Matched Skills"
            items={skillMatch?.matched}
            type="matched"
          />

          {/* Partial Skills */}

          <SkillSection
            title="Skills to Improve"
            items={skillMatch?.partial}
            type="partial"
          />

          {/* Missing Skills */}

          <SkillSection
            title="Missing Skills"
            items={
              jobMatch?.priority_missing_skills
            }
            type="missing"
          />

          {/* Job Information */}

          <div
            style={{
              background: "#ffffff",
              borderRadius: "20px",
              padding: "24px",
              boxShadow:
                "0 10px 35px rgba(0,0,0,0.08)",
            }}
          >
            <h3
              style={{
                marginTop: 0,
              }}
            >
              Job Information
            </h3>

            <p>
              <strong>
                Detected Title:
              </strong>{" "}
              {jobMatch?.job?.title ||
                "Not detected"}
            </p>

            <p>
              <strong>
                Title Match:
              </strong>{" "}
              {jobMatch?.title_match ?? 0}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
}) {
  return (
    <div
      style={{
        padding: "18px",
        borderRadius: "14px",
        background:
          "#f8fafc",
        border:
          "1px solid #e4e7ec",
      }}
    >
      <div
        style={{
          color: "#667085",
          fontSize: "14px",
          marginBottom: "6px",
        }}
      >
        {title}
      </div>

      <div
        style={{
          fontSize: "24px",
          fontWeight: 800,
          color: "#172033",
        }}
      >
        {value}
      </div>
    </div>
  );
}

function SkillSection({
  title,
  items = [],
  type,
}) {
  if (!items?.length) {
    return null;
  }

  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: "20px",
        padding: "24px",
        boxShadow:
          "0 10px 35px rgba(0,0,0,0.08)",
      }}
    >
      <h3
        style={{
          marginTop: 0,
          marginBottom: "16px",
        }}
      >
        {title}
      </h3>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        {items.map((item) => (
          <div
            key={
              item.skill_id ||
              item.id ||
              item.name
            }
            style={{
              padding:
                "9px 13px",
              borderRadius:
                "999px",
              background:
                type === "matched"
                  ? "#ecfdf3"
                  : type === "missing"
                  ? "#fff1f1"
                  : "#fffaeb",
              color:
                type === "matched"
                  ? "#027a48"
                  : type === "missing"
                  ? "#b42318"
                  : "#b54708",
              fontWeight: 600,
            }}
          >
            {item.name ||
              item.skill}
          </div>
        ))}
      </div>
    </div>
  );
}