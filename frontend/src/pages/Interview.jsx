import { useEffect, useMemo, useState } from "react";

import {
  getJobHistory,
  getMyCVs,
  startInterview,
  submitInterviewAnswer,
  completeInterview,
} from "../services/api";

import "./Interview.css";

function Interview() {
  const [jobAnalyses, setJobAnalyses] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");

  const [cvs, setCVs] = useState([]);
  const [selectedCV, setSelectedCV] = useState("");

  const [role, setRole] = useState("");

  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);

  const [scores, setScores] = useState([]);
  const [finalResult, setFinalResult] = useState(null);

  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);

  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  /* =========================================================
     LOAD INTERVIEW DATA
     ========================================================= */

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        setError("");

        const [cvData, jobData] = await Promise.all([
          getMyCVs(),
          getJobHistory(),
        ]);

        if (!mounted) return;

        const safeCVs = Array.isArray(cvData) ? cvData : [];
        const safeJobs = Array.isArray(jobData) ? jobData : [];

        setCVs(safeCVs);
        setJobAnalyses(safeJobs);

        if (safeCVs.length > 0) {
          setSelectedCV(String(safeCVs[0].id));
        }

        if (safeJobs.length > 0) {
          setSelectedJob(String(safeJobs[0].id));
        }
      } catch (err) {
        if (!mounted) return;
        setError(err?.message || "Failed to load interview setup.");
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

  /* =========================================================
     DERIVED DATA
     ========================================================= */

  const currentQuestion = questions[currentIndex];

  const answeredCount = scores.length;

  const totalQuestions = questions.length;

  const progressPercentage =
    totalQuestions > 0
      ? Math.round(
          ((currentIndex + (evaluation ? 1 : 0)) / totalQuestions) *
            100
        )
      : 0;

  const averageScore =
    scores.length > 0
      ? Math.round(
          scores.reduce((sum, score) => sum + score, 0) /
            scores.length
        )
      : 0;

  const currentScore = evaluation
    ? Number(evaluation.score) || 0
    : 0;

  const selectedCVObject = useMemo(
    () =>
      cvs.find(
        (cv) => String(cv.id) === String(selectedCV)
      ),
    [cvs, selectedCV]
  );

  const selectedJobObject = useMemo(
    () =>
      jobAnalyses.find(
        (job) => String(job.id) === String(selectedJob)
      ),
    [jobAnalyses, selectedJob]
  );

  const isLastQuestion =
    currentIndex + 1 >= questions.length;

  const roleIsReady = role.trim().length >= 2;

  const canStart =
    Boolean(selectedCV) &&
    roleIsReady &&
    !starting;

  /* =========================================================
     START INTERVIEW
     ========================================================= */

  const handleStart = async (e) => {
    e.preventDefault();

    setError("");

    if (!selectedCV) {
      setError("Please select a CV.");
      return;
    }

    if (!role.trim()) {
      setError("Please enter the target role.");
      return;
    }

    try {
      setStarting(true);

      const data = await startInterview(
        selectedCV,
        selectedJob || null,
        role.trim()
      );

      if (
        !data?.questions ||
        !Array.isArray(data.questions) ||
        data.questions.length === 0
      ) {
        throw new Error(
          "The AI did not generate any interview questions."
        );
      }

      setSessionId(data.session_id);
      setQuestions(data.questions);
      setCurrentIndex(0);

      setAnswer("");
      setEvaluation(null);
      setScores([]);
      setFinalResult(null);

      setStarted(true);
      setFinished(false);
    } catch (err) {
      setError(
        err?.message || "Failed to start the interview."
      );
    } finally {
      setStarting(false);
    }
  };

  /* =========================================================
     SUBMIT ANSWER
     ========================================================= */

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();

    const text = answer.trim();

    if (!text) {
      setError("Please write an answer before submitting.");
      return;
    }

    if (text.length < 10) {
      setError(
        "Please provide a little more detail in your answer."
      );
      return;
    }

    if (!currentQuestion) {
      setError("Question not found.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const data = await submitInterviewAnswer(
        currentQuestion.id,
        text
      );

      setEvaluation(data);

      setScores((prev) => [
        ...prev,
        Number(data?.score) || 0,
      ]);
    } catch (err) {
      setError(
        err?.message || "Failed to evaluate your answer."
      );
    } finally {
      setSubmitting(false);
    }
  };

  /* =========================================================
     NEXT / FINISH
     ========================================================= */

  const handleNext = async () => {
    setError("");

    if (
      currentIndex + 1 >=
      questions.length
    ) {
      if (!sessionId) {
        setError("Interview session not found.");
        return;
      }

      try {
        setSubmitting(true);

        const result =
          await completeInterview(sessionId);

        setFinalResult(result);
        setFinished(true);
      } catch (err) {
        setError(
          err?.message ||
            "Failed to complete the interview."
        );
      } finally {
        setSubmitting(false);
      }

      return;
    }

    setCurrentIndex((prev) => prev + 1);

    setAnswer("");
    setEvaluation(null);
  };

  /* =========================================================
     START ANOTHER INTERVIEW
     ========================================================= */

  const handleStartAnother = () => {
    setStarted(false);
    setFinished(false);

    setSessionId(null);
    setQuestions([]);
    setCurrentIndex(0);

    setAnswer("");
    setEvaluation(null);
    setScores([]);
    setFinalResult(null);

    setError("");
  };

  /* =========================================================
     CLEAR ERROR
     ========================================================= */

  const clearError = () => {
    setError("");
  };

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <div className="interview-page">
        <div className="page-loading">
          <div>
            <div className="loading-spinner" />
            <p>Loading interview setup...</p>
          </div>
        </div>
      </div>
    );
  }

  /* =========================================================
     FINAL RESULT
     ========================================================= */

  if (finished) {
    const finalScore =
      Number(finalResult?.final_score) ||
      averageScore;

    const completedQuestions =
      finalResult?.total_questions ??
      questions.length;

    return (
      <div className="interview-page">
        <div className="interview-complete">
          <div className="complete-icon">
            ✓
          </div>

          <div className="completion-badge">
            Interview Completed
          </div>

          <h2>Great Work! 🎉</h2>

          <p className="completion-description">
            You successfully completed your AI-powered
            interview for{" "}
            <strong>
              {role || "your target role"}
            </strong>.
          </p>

          <div className="final-score">
            <span>Overall Score</span>

            <strong>
              {finalScore}
              <small>/100</small>
            </strong>
          </div>

          <div className="final-stats">
            <div className="final-stat">
              <span>Questions</span>
              <strong>
                {completedQuestions}
              </strong>
            </div>

            <div className="final-stat">
              <span>Answered</span>
              <strong>
                {scores.length}
              </strong>
            </div>

            <div className="final-stat">
              <span>Average</span>
              <strong>
                {averageScore}
              </strong>
            </div>
          </div>

          <div className="result-message">
            {finalScore >= 85
              ? "Excellent performance! Your answers demonstrate strong interview readiness."
              : finalScore >= 70
              ? "Good performance! With a little more practice, you can become even stronger."
              : finalScore >= 50
              ? "You have a solid starting point. Focus on the AI feedback and keep practicing."
              : "Keep practicing. Use the feedback from this interview to improve your next attempt."}
          </div>

          <button
            className="primary-button"
            onClick={handleStartAnother}
          >
            Start Another Interview
          </button>
        </div>
      </div>
    );
  }

  /* =========================================================
     SETUP SCREEN
     ========================================================= */

  if (!started) {
    return (
      <div className="interview-page">
        <div className="page-header">
          <div>
            <span className="page-kicker">
              AI CAREER TOOLS
            </span>

            <h2>
              AI Interview Simulator
            </h2>

            <p>
              Practice realistic interview questions
              generated specifically for your CV,
              target role, and career direction.
            </p>
          </div>
        </div>

        {error && (
          <div className="error-message">
            <div>
              <strong>Something went wrong</strong>
              <span>{error}</span>
            </div>

            <button
              type="button"
              onClick={clearError}
              className="error-close"
              aria-label="Close error"
            >
              ×
            </button>
          </div>
        )}

        {cvs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              📄
            </div>

            <h3>No CV Available</h3>

            <p>
              Upload or create a CV before starting
              your AI interview.
            </p>

            <div className="empty-state-note">
              Your CV helps the AI generate more
              relevant interview questions.
            </div>
          </div>
        ) : (
          <>
            <div className="interview-intro-grid">
              <div className="intro-card">
                <span className="intro-card-icon">
                  AI
                </span>

                <div>
                  <strong>
                    AI-Generated Questions
                  </strong>

                  <p>
                    Questions are tailored to your
                    selected role and profile.
                  </p>
                </div>
              </div>

              <div className="intro-card">
                <span className="intro-card-icon">
                  ✓
                </span>

                <div>
                  <strong>
                    Real-Time Evaluation
                  </strong>

                  <p>
                    Get feedback and scoring after
                    every answer.
                  </p>
                </div>
              </div>

              <div className="intro-card">
                <span className="intro-card-icon">
                  ↗
                </span>

                <div>
                  <strong>
                    Improve Your Answers
                  </strong>

                  <p>
                    Review stronger versions of
                    your responses.
                  </p>
                </div>
              </div>
            </div>

            <section className="interview-start-card">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">
                    INTERVIEW SETUP
                  </span>

                  <h3>
                    Prepare Your Interview
                  </h3>

                  <p>
                    Choose the information the AI
                    should use to personalize your
                    interview.
                  </p>
                </div>

                <div className="setup-step-badge">
                  Step 1 of 1
                </div>
              </div>

              <form
                className="interview-start-form"
                onSubmit={handleStart}
              >
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="interview-cv">
                      Select CV
                    </label>

                    <select
                      id="interview-cv"
                      value={selectedCV}
                      onChange={(e) =>
                        setSelectedCV(
                          e.target.value
                        )
                      }
                    >
                      <option value="">
                        Select a CV
                      </option>

                      {cvs.map((cv) => (
                        <option
                          key={cv.id}
                          value={cv.id}
                        >
                          {cv.title}
                        </option>
                      ))}
                    </select>

                    {selectedCVObject && (
                      <small className="field-hint">
                        Using:{" "}
                        {selectedCVObject.title}
                      </small>
                    )}
                  </div>

                  <div className="form-group">
                    <label htmlFor="interview-job">
                      Select Job Analysis
                    </label>

                    <select
                      id="interview-job"
                      value={selectedJob}
                      onChange={(e) =>
                        setSelectedJob(
                          e.target.value
                        )
                      }
                    >
                      <option value="">
                        General Interview
                      </option>

                      {jobAnalyses.map((job) => (
                        <option
                          key={job.id}
                          value={job.id}
                        >
                          Job #{job.id} —{" "}
                          {job.final_match_score}%
                        </option>
                      ))}
                    </select>

                    {selectedJobObject && (
                      <small className="field-hint">
                        Match score:{" "}
                        {
                          selectedJobObject.final_match_score
                        }
                        %
                      </small>
                    )}
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="interview-role">
                    Target Role
                  </label>

                  <input
                    id="interview-role"
                    type="text"
                    value={role}
                    onChange={(e) =>
                      setRole(e.target.value)
                    }
                    placeholder="e.g. Python Backend Developer"
                    maxLength={120}
                  />

                  <div className="role-input-footer">
                    <small className="field-hint">
                      Be specific about the role
                      you're preparing for.
                    </small>

                    <span className="character-count">
                      {role.length}/120
                    </span>
                  </div>
                </div>

                <div className="selected-context">
                  <div className="context-item">
                    <span>CV</span>
                    <strong>
                      {selectedCVObject?.title ||
                        "Not selected"}
                    </strong>
                  </div>

                  <div className="context-divider" />

                  <div className="context-item">
                    <span>Job Focus</span>
                    <strong>
                      {selectedJobObject
                        ? `Analysis #${selectedJobObject.id}`
                        : "General Interview"}
                    </strong>
                  </div>

                  <div className="context-divider" />

                  <div className="context-item">
                    <span>Target</span>
                    <strong>
                      {role.trim() ||
                        "Not specified"}
                    </strong>
                  </div>
                </div>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={!canStart}
                >
                  {starting ? (
                    <>
                      <span className="button-spinner" />
                      Preparing Interview...
                    </>
                  ) : (
                    <>
                      Start Interview
                      <span>→</span>
                    </>
                  )}
                </button>
              </form>
            </section>
          </>
        )}
      </div>
    );
  }

  /* =========================================================
     ACTIVE INTERVIEW
     ========================================================= */

  return (
    <div className="interview-page">
      <div className="interview-header">
        <div>
          <span className="page-kicker">
            LIVE INTERVIEW
          </span>

          <h2>
            AI Interview Simulator
          </h2>

          <p>
            Answer naturally, explain your thinking,
            and use the AI feedback to improve.
          </p>
        </div>

        <div className="question-progress">
          <div className="progress-text">
            Question{" "}
            <strong>
              {currentIndex + 1}
            </strong>{" "}
            of{" "}
            <strong>
              {questions.length}
            </strong>
          </div>

          <div className="progress-bar">
            <span
              style={{
                width: `${Math.min(
                  progressPercentage,
                  100
                )}%`,
              }}
            />
          </div>

          <small>
            {Math.min(
              progressPercentage,
              100
            )}
            % complete
          </small>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <div>
            <strong>Something went wrong</strong>
            <span>{error}</span>
          </div>

          <button
            type="button"
            onClick={clearError}
            className="error-close"
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      <div className="interview-context-bar">
        <div className="context-item">
          <span>Target Role</span>
          <strong>
            {role || "General"}
          </strong>
        </div>

        <div className="context-divider" />

        <div className="context-item">
          <span>CV</span>
          <strong>
            {selectedCVObject?.title ||
              "Selected CV"}
          </strong>
        </div>

        <div className="context-divider" />

        <div className="context-item">
          <span>Answered</span>
          <strong>
            {answeredCount}/{totalQuestions}
          </strong>
        </div>

        {scores.length > 0 && (
          <>
            <div className="context-divider" />

            <div className="context-item">
              <span>Average Score</span>
              <strong>
                {averageScore}/100
              </strong>
            </div>
          </>
        )}
      </div>

      <section className="question-card">
        <div className="question-card-top">
          <div className="question-number">
            Question {currentIndex + 1}
          </div>

          {evaluation && (
            <div
              className={`question-status ${
                currentScore >= 70
                  ? "positive"
                  : "needs-improvement"
              }`}
            >
              {currentScore >= 70
                ? "Strong Answer"
                : "Needs Improvement"}
            </div>
          )}
        </div>

        <h3>
          {currentQuestion?.question}
        </h3>

        <div className="answer-guidance">
          <span>💡</span>

          <p>
            Take your time. A clear answer with
            specific examples is usually stronger
            than a very short response.
          </p>
        </div>

        <form onSubmit={handleSubmitAnswer}>
          <div className="textarea-wrapper">
            <textarea
              value={answer}
              onChange={(e) =>
                setAnswer(e.target.value)
              }
              placeholder="Write your answer here..."
              rows={9}
              disabled={
                submitting || Boolean(evaluation)
              }
              maxLength={5000}
            />

            <div className="textarea-footer">
              <span>
                {answer.length}/5000 characters
              </span>

              {!evaluation && (
                <span>
                  Minimum recommended: 10 characters
                </span>
              )}
            </div>
          </div>

          {!evaluation && (
            <button
              type="submit"
              className="primary-button"
              disabled={
                submitting ||
                !answer.trim()
              }
            >
              {submitting ? (
                <>
                  <span className="button-spinner" />
                  AI is evaluating...
                </>
              ) : (
                <>
                  Submit Answer
                  <span>→</span>
                </>
              )}
            </button>
          )}
        </form>
      </section>

      {evaluation && (
        <section className="evaluation-card">
          <div className="evaluation-header">
            <div>
              <span className="section-kicker">
                AI EVALUATION
              </span>

              <h3>
                Here's how you performed
              </h3>
            </div>

            <div
              className={`evaluation-score ${
                currentScore >= 80
                  ? "excellent"
                  : currentScore >= 65
                  ? "good"
                  : currentScore >= 50
                  ? "average"
                  : "needs-work"
              }`}
            >
              <span>Your Score</span>

              <strong>
                {currentScore}
                <small>/100</small>
              </strong>
            </div>
          </div>

          <div className="score-progress">
            <div
              className="score-progress-fill"
              style={{
                width: `${Math.min(
                  currentScore,
                  100
                )}%`,
              }}
            />
          </div>

          <div className="feedback-block">
            <div className="feedback-heading">
              <span className="feedback-icon">
                AI
              </span>

              <h3>AI Feedback</h3>
            </div>

            <p>
              {evaluation.feedback ||
                "No feedback was provided."}
            </p>
          </div>

          {evaluation.improved_answer && (
            <div className="feedback-block improved-answer">
              <div className="feedback-heading">
                <span className="feedback-icon">
                  ↗
                </span>

                <h3>
                  Improved Answer
                </h3>
              </div>

              <p>
                {evaluation.improved_answer}
              </p>
            </div>
          )}

          <div className="evaluation-actions">
            <div className="evaluation-tip">
              <strong>
                Keep this feedback in mind
              </strong>

              <span>
                Apply it to your next answer.
              </span>
            </div>

            <button
              className="primary-button"
              onClick={handleNext}
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <span className="button-spinner" />
                  Finishing...
                </>
              ) : isLastQuestion ? (
                <>
                  Finish Interview
                  <span>✓</span>
                </>
              ) : (
                <>
                  Next Question
                  <span>→</span>
                </>
              )}
            </button>
          </div>
        </section>
      )}

      {!evaluation && (
        <div className="interview-hint">
          <span>Tip</span>
          <p>
            Focus on the question, answer with
            specific examples, and explain the
            reasoning behind your decisions.
          </p>
        </div>
      )}
    </div>
  );
}

export default Interview;