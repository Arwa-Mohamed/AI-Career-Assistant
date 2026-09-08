import { useEffect, useMemo, useState } from "react";

import {
  createCareerProject,
  getCareerProjects,
  updateCareerProject,
  deleteCareerProject,
  getProjectRecommendations,
  getCVs,
  addProjectToCV,
} from "../services/api";

import "./Projects.css";

function Projects() {
  const [projects, setProjects] = useState([]);
  const [cvs, setCVs] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [recommendationMessage, setRecommendationMessage] = useState("");
  const [editingProjectId, setEditingProjectId] = useState(null);
  const [editGithub, setEditGithub] = useState("");
  const [editDemo, setEditDemo] = useState("");
  const [addingToCV, setAddingToCV] = useState(null);
  const [deletingProjectId, setDeletingProjectId] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: "",
    description: "",
    target_role: "",
    skills: "",
    objectives: "",
    difficulty: "beginner",
    estimated_days: 7,
  });

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError("");

      const [projectData, cvData] = await Promise.all([
        getCareerProjects(),
        getCVs(),
      ]);

      setProjects(Array.isArray(projectData) ? projectData : []);
      setCVs(Array.isArray(cvData) ? cvData : []);
    } catch (err) {
      setError(err?.message || "Failed to load projects.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const projectStats = useMemo(() => {
    const total = projects.length;
    const completed = projects.filter(
      (project) => project.status === "completed"
    ).length;
    const inProgress = projects.filter(
      (project) => project.status === "in_progress"
    ).length;
    const notStarted = projects.filter(
      (project) => project.status === "not_started"
    ).length;

    const averageProgress =
      total > 0
        ? Math.round(
            projects.reduce(
              (sum, project) =>
                sum +
                Math.min(
                  Math.max(Number(project.progress) || 0, 0),
                  100
                ),
              0
            ) / total
          )
        : 0;

    return {
      total,
      completed,
      inProgress,
      notStarted,
      averageProgress,
    };
  }, [projects]);

  const handleGenerateRecommendations = async () => {
    try {
      setLoadingRecommendations(true);
      setError("");
      setSuccessMessage("");
      setRecommendationMessage("");

      const data = await getProjectRecommendations();

      setRecommendations(
        Array.isArray(data?.recommendations) ? data.recommendations : []
      );
      setRecommendationMessage(data?.message || "");
    } catch (err) {
      setError(
        err?.message || "Failed to generate project recommendations."
      );
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleAddRecommendedProject = async (project) => {
    try {
      setError("");
      setSuccessMessage("");

      const created = await createCareerProject({
        title: project.title,
        description: project.description,
        target_role: project.target_role || "",
        skills: project.skills || [],
        objectives: project.objectives || [],
        difficulty: project.difficulty || "beginner",
        estimated_days: project.estimated_days || 7,
      });

      setProjects((prev) => [created, ...prev]);
      setRecommendations((prev) =>
        prev.filter((item) => item.title !== project.title)
      );

      setSuccessMessage(`"${project.title}" added to your projects.`);
    } catch (err) {
      setError(err?.message || "Failed to save recommended project.");
    }
  };

  const openCreateForm = () => {
    setCreateForm({
      title: "",
      description: "",
      target_role: "",
      skills: "",
      objectives: "",
      difficulty: "beginner",
      estimated_days: 7,
    });
    setShowCreateForm(true);
    setError("");
    setSuccessMessage("");
  };

  const closeCreateForm = () => {
    setShowCreateForm(false);
  };

  const handleCreateProject = async (event) => {
    event.preventDefault();

    const title = createForm.title.trim();
    const description = createForm.description.trim();
    const targetRole = createForm.target_role.trim();
    const skills = createForm.skills
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean);
    const objectives = createForm.objectives
      .split("\n")
      .map((objective) => objective.trim())
      .filter(Boolean);
    const estimatedDays = Math.max(1, Number(createForm.estimated_days) || 7);

    if (!title) {
      setError("Project title is required.");
      return;
    }

    try {
      setError("");
      setSuccessMessage("");

      const created = await createCareerProject({
        title,
        description,
        target_role: targetRole,
        skills,
        objectives,
        difficulty: createForm.difficulty || "beginner",
        estimated_days: estimatedDays,
      });

      setProjects((prev) => [created, ...prev]);
      setShowCreateForm(false);
      setSuccessMessage(`"${created.title || title}" was added to your projects.`);
    } catch (err) {
      setError(err?.message || "Failed to create project.");
    }
  };

  const handleDeleteProject = async (project) => {
    if (!project?.id) return;

    const confirmed = window.confirm(
      `Delete "${project.title}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      setDeletingProjectId(project.id);
      setError("");
      setSuccessMessage("");

      await deleteCareerProject(project.id);

      setProjects((prev) =>
        prev.filter((item) => item.id !== project.id)
      );

      if (editingProjectId === project.id) {
        setEditingProjectId(null);
        setEditGithub("");
        setEditDemo("");
      }

      setSuccessMessage(`"${project.title}" was deleted.`);
    } catch (err) {
      setError(err?.message || "Failed to delete project.");
    } finally {
      setDeletingProjectId(null);
    }
  };

  const handleStatusChange = async (projectId, status) => {
    try {
      setError("");
      setSuccessMessage("");

      const updated = await updateCareerProject(projectId, { status });

      setProjects((prev) =>
        prev.map((project) =>
          project.id === projectId ? updated : project
        )
      );

      if (status === "completed") {
        setSuccessMessage(
          "Project completed successfully. You can now add it to your CV."
        );
      } else if (status === "in_progress") {
        setSuccessMessage("Project marked as in progress.");
      } else {
        setSuccessMessage("Project moved back to not started.");
      }
    } catch (err) {
      setError(err?.message || "Failed to update project.");
    }
  };

  const startEditingLinks = (project) => {
    setEditingProjectId(project.id);
    setEditGithub(project.github_url || "");
    setEditDemo(project.demo_url || "");
    setError("");
    setSuccessMessage("");
  };

  const savePortfolioLinks = async (projectId) => {
    const github = editGithub.trim();
    const demo = editDemo.trim();

    if (github && !/^https?:\/\/.+/i.test(github)) {
      setError("GitHub URL must start with http:// or https://.");
      return;
    }

    if (demo && !/^https?:\/\/.+/i.test(demo)) {
      setError("Live Demo URL must start with http:// or https://.");
      return;
    }

    try {
      setError("");
      setSuccessMessage("");

      const updated = await updateCareerProject(projectId, {
        github_url: github,
        demo_url: demo,
      });

      setProjects((prev) =>
        prev.map((project) =>
          project.id === projectId ? updated : project
        )
      );

      setEditingProjectId(null);
      setEditGithub("");
      setEditDemo("");

      setSuccessMessage("Portfolio links saved successfully.");
    } catch (err) {
      setError(err?.message || "Failed to save project links.");
    }
  };

  const handleAddProjectToCV = async (project) => {
    try {
      setError("");
      setSuccessMessage("");

      if (!project || project.status !== "completed") {
        throw new Error(
          "Only completed projects can be added to your CV."
        );
      }

      if (cvs.length === 0) {
        throw new Error(
          "Please upload a CV first before adding a project to it."
        );
      }

      const latestCV = cvs[0];
      setAddingToCV(project.id);

      const result = await addProjectToCV(latestCV.id, project.id);

      setSuccessMessage(
        result?.message || "Project added to your CV successfully."
      );
    } catch (err) {
      setError(err?.message || "Failed to add project to CV.");
    } finally {
      setAddingToCV(null);
    }
  };

  const cancelEditingLinks = () => {
    setEditingProjectId(null);
    setEditGithub("");
    setEditDemo("");
  };

  const statusLabel = {
    not_started: "Not Started",
    in_progress: "In Progress",
    completed: "Completed",
  };

  const getDifficultyClass = (difficulty) => {
    const value = String(difficulty || "beginner").toLowerCase();

    if (value.includes("advanced") || value.includes("expert")) {
      return "advanced";
    }

    if (value.includes("intermediate")) {
      return "intermediate";
    }

    return "beginner";
  };

  if (loading) {
    return (
      <div className="projects-page">
        <div className="projects-loading">
          <div className="loading-spinner" />
          <p>Loading your projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="projects-page">
      <div className="projects-header">
        <div>
          <span className="projects-eyebrow">CAREER DEVELOPMENT</span>
          <h1>My Projects</h1>
          <p>
            Turn your skill gaps into practical experience and portfolio
            evidence.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={handleGenerateRecommendations}
          disabled={loadingRecommendations}
        >
          {loadingRecommendations ? "Analyzing..." : "Generate Projects →"}
        </button>

        <button
          type="button"
          className="secondary-button"
          onClick={openCreateForm}
        >
          + New Project
        </button>
      </div>

      {error && (
        <div className="projects-error" role="alert">
          <div>
            <strong>Something went wrong</strong>
            <span>{error}</span>
          </div>
          <button
            type="button"
            className="projects-message-close"
            onClick={() => setError("")}
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      {successMessage && (
        <div className="projects-success" role="status">
          <span>✓</span>
          <div>{successMessage}</div>
          <button
            type="button"
            className="projects-message-close"
            onClick={() => setSuccessMessage("")}
            aria-label="Close message"
          >
            ×
          </button>
        </div>
      )}

      <div className="projects-overview">
        <div className="overview-card">
          <span>Total Projects</span>
          <strong>{projectStats.total}</strong>
          <small>Across your career workspace</small>
        </div>

        <div className="overview-card completed">
          <span>Completed</span>
          <strong>{projectStats.completed}</strong>
          <small>Portfolio-ready projects</small>
        </div>

        <div className="overview-card progress">
          <span>In Progress</span>
          <strong>{projectStats.inProgress}</strong>
          <small>Currently being built</small>
        </div>

        <div className="overview-card readiness">
          <span>Average Progress</span>
          <strong>{projectStats.averageProgress}%</strong>
          <small>Overall project completion</small>
        </div>
      </div>

      <section className="recommendations-section">
        <div className="recommendations-header">
          <div>
            <span className="projects-eyebrow">SMART RECOMMENDATIONS</span>
            <h2>Projects For Your Career Goals</h2>
            <p>
              Get project ideas from your CV and career direction. Analyze a
              job to make recommendations more specific to its requirements
              and skill gaps.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={handleGenerateRecommendations}
            disabled={loadingRecommendations}
          >
            {loadingRecommendations ? (
              <>
                <span className="button-spinner" />
                Analyzing...
              </>
            ) : (
              <>Generate Projects <span>→</span></>
            )}
          </button>
        </div>

        {recommendationMessage && (
          <div className="recommendation-message">
            <span>✦</span>
            {recommendationMessage}
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="recommendations-grid">
            {recommendations.map((project, index) => (
              <div
                className="recommendation-card"
                key={`${project.title}-${index}`}
              >
                <div className="recommendation-card-top">
                  <div className="recommendation-number">{index + 1}</div>
                  <span
                    className={`project-difficulty ${getDifficultyClass(
                      project.difficulty
                    )}`}
                  >
                    {project.difficulty || "beginner"}
                  </span>
                </div>

                <h3>{project.title}</h3>
                <p>
                  {project.description ||
                    "No project description available."}
                </p>

                {project.target_role && (
                  <div className="project-target-role">
                    <span>Target Role</span>
                    <strong>{project.target_role}</strong>
                  </div>
                )}

                {project.matched_gap && (
                  <div className="matched-gap">
                    <strong>Skill Gap</strong>
                    <span>{project.matched_gap}</span>
                  </div>
                )}

                {project.skills?.length > 0 && (
                  <div className="project-skills">
                    {project.skills.map((skill) => (
                      <span key={skill}>{skill}</span>
                    ))}
                  </div>
                )}

                <div className="recommendation-objectives">
                  <strong>What you'll practice</strong>
                  {project.objectives?.length > 0 && (
                    <ul>
                      {project.objectives.slice(0, 4).map(
                        (objective, objectiveIndex) => (
                          <li key={`${objective}-${objectiveIndex}`}>
                            <span>✓</span>
                            {objective}
                          </li>
                        )
                      )}
                    </ul>
                  )}
                </div>

                <div className="recommendation-footer">
                  <span className="estimated-days">
                    <span>⏱</span>
                    {project.estimated_days || 7} days
                  </span>

                  <button
                    className="secondary-button"
                    onClick={() => handleAddRecommendedProject(project)}
                  >
                    Add to My Projects
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loadingRecommendations &&
          recommendations.length === 0 &&
          recommendationMessage && (
            <div className="recommendations-empty">
              No new project recommendations are available right now.
            </div>
          )}
      </section>

      <section className="my-projects-section">
        <div className="projects-section-heading">
          <div>
            <span className="projects-eyebrow">YOUR WORK</span>
            <h2>My Projects</h2>
            <p>Build, complete, and showcase your practical experience.</p>
          </div>

          {projects.length > 0 && (
            <div className="projects-filter-summary">
              <span>{projectStats.notStarted} not started</span>
              <span>{projectStats.inProgress} in progress</span>
              <span>{projectStats.completed} completed</span>
            </div>
          )}
        </div>

        {projects.length === 0 ? (
          <div className="projects-empty">
            <div className="projects-empty-icon">🚀</div>
            <span className="projects-eyebrow">START BUILDING</span>
            <h2>Start building your portfolio</h2>
            <p>
              Generate projects from your CV and career goals, then build the
              ones that strengthen your profile.
            </p>
            <div className="empty-actions">
              <button
                className="primary-button"
                onClick={handleGenerateRecommendations}
                disabled={loadingRecommendations}
              >
                Find Projects For Me <span>→</span>
              </button>

              <button
                className="secondary-button"
                onClick={openCreateForm}
              >
                Create Project Manually
              </button>
            </div>
          </div>
        ) : (
          <div className="projects-grid">
            {projects.map((project) => {
              const progress = Math.min(
                Math.max(Number(project.progress) || 0, 0),
                100
              );

              const isEditing = editingProjectId === project.id;
              const isCompleted = project.status === "completed";
              const isAdding = addingToCV === project.id;
              const isDeleting = deletingProjectId === project.id;
              const difficultyClass = getDifficultyClass(project.difficulty);
              const objectives = Array.isArray(project.objectives)
                ? project.objectives
                : [];
              const skills = Array.isArray(project.skills) ? project.skills : [];

              return (
                <article className="project-card" key={project.id}>
                  <div className="project-card-top">
                    <div>
                      <span
                        className={`project-difficulty ${difficultyClass}`}
                      >
                        {project.difficulty || "beginner"}
                      </span>
                      <h2>{project.title}</h2>
                    </div>

                    <div className="project-card-actions-top">
                      <span className={`project-status ${project.status}`}>
                        {statusLabel[project.status] || "Not Started"}
                      </span>

                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => handleDeleteProject(project)}
                        disabled={isDeleting}
                      >
                        {isDeleting ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>

                  <p className="project-description">
                    {project.description || "No description available."}
                  </p>

                  {project.target_role && (
                    <div className="project-target-role">
                      <span>Target Role</span>
                      <strong>{project.target_role}</strong>
                    </div>
                  )}

                  {skills.length > 0 && (
                    <div className="project-skills">
                      {skills.map((skill) => (
                        <span key={skill}>{skill}</span>
                      ))}
                    </div>
                  )}

                  {objectives.length > 0 && (
                    <div className="project-objectives">
                      <div className="project-objectives-heading">
                        <strong>Objectives</strong>
                        <span>{objectives.length}</span>
                      </div>

                      <ul>
                        {objectives.slice(0, 4).map(
                          (objective, objectiveIndex) => (
                            <li key={`${objective}-${objectiveIndex}`}>
                              <span>✓</span>
                              {objective}
                            </li>
                          )
                        )}
                      </ul>

                      {objectives.length > 4 && (
                        <small>+{objectives.length - 4} more objectives</small>
                      )}
                    </div>
                  )}

                  <div className="project-progress">
                    <div className="project-progress-top">
                      <span>Progress</span>
                      <strong>{progress}%</strong>
                    </div>
                    <div className="project-progress-bar">
                      <div style={{ width: `${progress}%` }} />
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="portfolio-links-editor">
                      <div className="editor-heading">
                        <span className="projects-eyebrow">PORTFOLIO</span>
                        <h4>Add your project links</h4>
                        <p>Connect employers directly to your work.</p>
                      </div>

                      <div className="form-group">
                        <label>GitHub URL</label>
                        <input
                          type="url"
                          value={editGithub}
                          onChange={(e) => setEditGithub(e.target.value)}
                          placeholder="https://github.com/username/project"
                        />
                      </div>

                      <div className="form-group">
                        <label>Live Demo URL</label>
                        <input
                          type="url"
                          value={editDemo}
                          onChange={(e) => setEditDemo(e.target.value)}
                          placeholder="https://your-project.com"
                        />
                      </div>

                      <div className="portfolio-editor-actions">
                        <button
                          type="button"
                          className="primary-button"
                          onClick={() => savePortfolioLinks(project.id)}
                        >
                          Save Links
                        </button>

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={cancelEditingLinks}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="portfolio-links">
                      {project.github_url && (
                        <a
                          href={project.github_url}
                          target="_blank"
                          rel="noreferrer"
                          className="portfolio-link"
                        >
                          GitHub ↗
                        </a>
                      )}

                      {project.demo_url && (
                        <a
                          href={project.demo_url}
                          target="_blank"
                          rel="noreferrer"
                          className="portfolio-link"
                        >
                          Live Demo ↗
                        </a>
                      )}

                      <button
                        type="button"
                        className="link-button"
                        onClick={() => startEditingLinks(project)}
                      >
                        {project.github_url || project.demo_url
                          ? "Edit Links"
                          : "Add Portfolio Links"}
                      </button>
                    </div>
                  )}

                  <div className="project-actions">
                    {!isCompleted && (
                      <>
                        {project.status !== "in_progress" && (
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                              handleStatusChange(project.id, "in_progress")
                            }
                          >
                            Start
                          </button>
                        )}

                        <button
                          type="button"
                          className="primary-button"
                          onClick={() =>
                            handleStatusChange(project.id, "completed")
                          }
                        >
                          Complete
                        </button>
                      </>
                    )}

                    {isCompleted && (
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => handleAddProjectToCV(project)}
                        disabled={isAdding}
                      >
                        {isAdding ? "Adding..." : "Add to CV"}
                      </button>
                    )}
                  </div>

                  {isCompleted && (
                    <div className="completed-project-footer">
                      <span>✓ Portfolio-ready</span>
                      <span>Ready to showcase</span>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>

      {showCreateForm && (
        <div
          className="project-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeCreateForm();
            }
          }}
        >
          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-project-title"
          >
            <div className="project-modal-header">
              <div>
                <span className="projects-eyebrow">NEW PROJECT</span>
                <h2 id="create-project-title">Create a project</h2>
                <p>Add your own project without relying on AI recommendations.</p>
              </div>

              <button
                type="button"
                className="projects-message-close"
                onClick={closeCreateForm}
                aria-label="Close create project form"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="project-create-form">
              <div className="form-group">
                <label htmlFor="project-title">Project Title *</label>
                <input
                  id="project-title"
                  type="text"
                  value={createForm.title}
                  onChange={(event) =>
                    setCreateForm((prev) => ({ ...prev, title: event.target.value }))
                  }
                  placeholder="e.g. Customer Churn Analysis"
                  autoFocus
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="project-description">Description</label>
                <textarea
                  id="project-description"
                  rows="4"
                  value={createForm.description}
                  onChange={(event) =>
                    setCreateForm((prev) => ({
                      ...prev,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Describe what you are building and why it matters."
                />
              </div>

              <div className="project-create-grid">
                <div className="form-group">
                  <label htmlFor="project-role">Target Role</label>
                  <input
                    id="project-role"
                    type="text"
                    value={createForm.target_role}
                    onChange={(event) =>
                      setCreateForm((prev) => ({
                        ...prev,
                        target_role: event.target.value,
                      }))
                    }
                    placeholder="e.g. Data Analyst"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="project-difficulty">Difficulty</label>
                  <select
                    id="project-difficulty"
                    value={createForm.difficulty}
                    onChange={(event) =>
                      setCreateForm((prev) => ({
                        ...prev,
                        difficulty: event.target.value,
                      }))
                    }
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="project-days">Estimated Days</label>
                  <input
                    id="project-days"
                    type="number"
                    min="1"
                    value={createForm.estimated_days}
                    onChange={(event) =>
                      setCreateForm((prev) => ({
                        ...prev,
                        estimated_days: event.target.value,
                      }))
                    }
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="project-skills">Skills</label>
                <input
                  id="project-skills"
                  type="text"
                  value={createForm.skills}
                  onChange={(event) =>
                    setCreateForm((prev) => ({ ...prev, skills: event.target.value }))
                  }
                  placeholder="SQL, Power BI, DAX, Excel"
                />
                <small>Separate skills with commas.</small>
              </div>

              <div className="form-group">
                <label htmlFor="project-objectives">Objectives</label>
                <textarea
                  id="project-objectives"
                  rows="5"
                  value={createForm.objectives}
                  onChange={(event) =>
                    setCreateForm((prev) => ({
                      ...prev,
                      objectives: event.target.value,
                    }))
                  }
                  placeholder={'Build the dashboard\nAnalyze business KPIs\nPresent actionable insights'}
                />
                <small>Write one objective per line.</small>
              </div>

              <div className="portfolio-editor-actions">
                <button type="submit" className="primary-button">
                  Create Project
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeCreateForm}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Projects;
