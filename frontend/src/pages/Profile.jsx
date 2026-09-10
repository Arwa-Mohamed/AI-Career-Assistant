import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AccountSecurity from "../components/AccountSecurity/AccountSecurity";

import {
  getProfile,
  updateProfile,
  updateProfileImage,
  getCareerProjects,
} from "../services/api";

import "./Profile.css";

// =========================================================
// API URL
// =========================================================

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


// =========================================================
// MEDIA URL
// =========================================================

function getMediaUrl(imageUrl) {
  if (!imageUrl) {
    return "";
  }

  if (
    imageUrl.startsWith("http://") ||
    imageUrl.startsWith("https://")
  ) {
    return imageUrl;
  }

  if (imageUrl.startsWith("/")) {
    return `${API_URL}${imageUrl}`;
  }

  return `${API_URL}/${imageUrl}`;
}


// =========================================================
// PROFILE COMPONENT
// =========================================================

function Profile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState({
    full_name: "",
    phone: "",
    location: "",
    bio: "",
    career_goal: "",
    linkedin_url: "",
    profile_image: "",
  });

  const [account, setAccount] = useState({
    username: "",
    email: "",
  });

  const [projects, setProjects] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  const [imagePreview, setImagePreview] = useState("");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  // =========================================================
  // LOAD PROFILE + ACCOUNT + PROJECTS
  // =========================================================

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        setError("");

        const [profileData, projectData] =
          await Promise.all([
            getProfile(),
            getCareerProjects(),
          ]);

        if (!mounted) {
          return;
        }

        const accountUsername =
          profileData?.username || "";

        const accountEmail =
          profileData?.email || "";

        const accountFullName =
          profileData?.account_full_name || "";

        const savedFullName =
          profileData?.full_name || "";

        /*
         * Priority:
         * 1. Explicit profile full name
         * 2. User account full name
         * 3. Username
         */

        const resolvedFullName =
          savedFullName ||
          accountFullName ||
          accountUsername ||
          "";

        const savedProfileImage =
          getMediaUrl(
            profileData?.profile_image || ""
          );

        setAccount({
          username: accountUsername,
          email: accountEmail,
        });

        setProfile({
          full_name: resolvedFullName,

          phone:
            profileData?.phone || "",

          location:
            profileData?.location || "",

          bio:
            profileData?.bio || "",

          career_goal:
            profileData?.career_goal || "",

          linkedin_url:
            profileData?.linkedin_url || "",

          profile_image:
            savedProfileImage,
        });

        setImagePreview(
          savedProfileImage
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
            "Failed to load profile."
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
  // HANDLE INPUT
  // =========================================================

  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setProfile((previous) => ({
      ...previous,
      [name]: value,
    }));

    if (message) {
      setMessage("");
    }

    if (error) {
      setError("");
    }
  };


  // =========================================================
  // HANDLE PROFILE IMAGE
  // =========================================================

  const handleImageChange = async (
    event
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");
    setMessage("");

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError(
        "Please upload a JPG, JPEG, PNG, or WEBP image."
      );

      event.target.value = "";
      return;
    }

    const maxSize =
      2 * 1024 * 1024;

    if (file.size > maxSize) {
      setError(
        "Profile image size must not exceed 2 MB."
      );

      event.target.value = "";
      return;
    }

    const previousImage =
      profile.profile_image || "";

    const localPreview =
      URL.createObjectURL(file);

    setImagePreview(localPreview);

    try {
      setUploadingImage(true);

      const data =
        await updateProfileImage(
          file
        );

      const uploadedImage =
        getMediaUrl(
          data?.profile_image || ""
        );

      setProfile((previous) => ({
        ...previous,
        profile_image:
          uploadedImage ||
          previous.profile_image ||
          "",
      }));

      if (uploadedImage) {
        setImagePreview(
          uploadedImage
        );
      }

      setMessage(
        "Profile photo updated successfully."
      );
    } catch (err) {
      setImagePreview(
        previousImage
      );

      setError(
        err?.message ||
          "Failed to upload profile image."
      );
    } finally {
      setUploadingImage(false);

      URL.revokeObjectURL(
        localPreview
      );

      event.target.value = "";
    }
  };


  // =========================================================
  // SAVE PROFILE
  // =========================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      setMessage("");

      const data = await updateProfile({
        full_name:
          profile.full_name,

        phone:
          profile.phone,

        location:
          profile.location,

        bio:
          profile.bio,

        career_goal:
          profile.career_goal,

        linkedin_url:
          profile.linkedin_url,
      });

      setProfile((previous) => ({
        ...previous,

        full_name:
          data?.full_name ||
          profile.full_name ||
          account.username ||
          "",

        phone:
          data?.phone ??
          profile.phone ??
          "",

        location:
          data?.location ??
          profile.location ??
          "",

        bio:
          data?.bio ??
          profile.bio ??
          "",

        career_goal:
          data?.career_goal ??
          profile.career_goal ??
          "",

        linkedin_url:
          data?.linkedin_url ??
          profile.linkedin_url ??
          "",

        profile_image:
          getMediaUrl(
            data?.profile_image ||
              previous.profile_image ||
              ""
          ),
      }));

      const returnedImage =
        getMediaUrl(
          data?.profile_image ||
            profile.profile_image ||
            ""
        );

      if (returnedImage) {
        setImagePreview(
          returnedImage
        );
      }

      setAccount((previous) => ({
        username:
          data?.username ||
          previous.username,

        email:
          data?.email ||
          previous.email,
      }));

      setMessage(
        "Profile updated successfully."
      );

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (err) {
      setError(
        err?.message ||
          "Failed to update profile."
      );
    } finally {
      setSaving(false);
    }
  };


  // =========================================================
  // PROFILE COMPLETENESS
  // =========================================================

  const profileFields = useMemo(
    () => [
      {
        label: "Full Name",
        value: profile.full_name,
      },
      {
        label: "Phone",
        value: profile.phone,
      },
      {
        label: "Location",
        value: profile.location,
      },
      {
        label: "About You",
        value: profile.bio,
      },
      {
        label: "Career Goal",
        value: profile.career_goal,
      },
      {
        label: "LinkedIn",
        value: profile.linkedin_url,
      },
    ],
    [profile]
  );

  const completedFields =
    profileFields.filter(
      (field) =>
        field.value &&
        String(field.value).trim() !== ""
    ).length;

  const profileCompleteness =
    profileFields.length > 0
      ? Math.round(
          (completedFields /
            profileFields.length) *
            100
        )
      : 0;

  const remainingFields =
    profileFields.filter(
      (field) =>
        !field.value ||
        String(field.value).trim() === ""
    );


  // =========================================================
  // DISPLAY DATA
  // =========================================================

  const displayName =
    profile.full_name.trim() ||
    account.username.trim() ||
    "Career Explorer";

  const avatarLetter =
    displayName
      .charAt(0)
      .toUpperCase() || "A";

  const displayGoal =
    profile.career_goal ||
    "Add your career goal";

  const hasProfileImage =
    Boolean(imagePreview);


  // =========================================================
  // PROJECTS
  // =========================================================

  const completedProjects =
    projects.filter(
      (project) =>
        project.status === "completed"
    );

  const activeProjects =
    projects.filter(
      (project) =>
        project.status === "in_progress"
    );

  const plannedProjects =
    projects.filter(
      (project) =>
        project.status === "not_started"
    );

  const totalProjects =
    projects.length;

  const projectCompletionRate =
    totalProjects > 0
      ? Math.round(
          (completedProjects.length /
            totalProjects) *
            100
        )
      : 0;

  const latestProjects = [
    ...projects,
  ]
    .sort(
      (a, b) =>
        Number(b?.id || 0) -
        Number(a?.id || 0)
    )
    .slice(0, 4);


  // =========================================================
  // PROFILE STRENGTH
  // =========================================================

  let profileStrengthLabel =
    "Getting Started";

  let profileStrengthDescription =
    "Complete your profile so the platform can personalize your career journey.";

  if (profileCompleteness >= 90) {
    profileStrengthLabel =
      "Excellent";

    profileStrengthDescription =
      "Your professional profile is highly complete and ready to support personalized recommendations.";
  } else if (profileCompleteness >= 75) {
    profileStrengthLabel =
      "Strong";

    profileStrengthDescription =
      "Your profile is strong. Completing the remaining details will make your career recommendations more precise.";
  } else if (profileCompleteness >= 50) {
    profileStrengthLabel =
      "Developing";

    profileStrengthDescription =
      "Your profile has a solid foundation, but several details are still missing.";
  } else if (profileCompleteness >= 25) {
    profileStrengthLabel =
      "Building";

    profileStrengthDescription =
      "Add more professional information so the AI can better understand your career goals.";
  }


  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {
    return (
      <div className="profile-page">

        <div className="profile-loading">

          <div className="profile-loading-spinner" />

          <div>
            <strong>
              Loading your profile
            </strong>

            <span>
              Preparing your career information...
            </span>
          </div>

        </div>

      </div>
    );
  }


  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="profile-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <header className="profile-header">

        <div className="profile-header-content">

          <span className="profile-eyebrow">
            PERSONAL PROFILE
          </span>

          <h1>
            My Profile
          </h1>

          <p>
            Manage the information that powers
            your personalized career experience.
          </p>

        </div>

        <div className="profile-header-actions">

          <button
            type="button"
            className="profile-secondary-button"
            onClick={() =>
              navigate("/dashboard")
            }
          >
            ← Dashboard
          </button>

          <button
            type="button"
            className="profile-primary-button"
            onClick={() =>
              navigate("/cv-builder")
            }
          >
            Build My CV
          </button>

        </div>

      </header>


      {/* =====================================================
          MESSAGES
      ===================================================== */}

      {message && (
        <div className="profile-success-message">

          <span className="profile-message-icon">
            ✓
          </span>

          <span>
            {message}
          </span>

        </div>
      )}

      {error && (
        <div className="profile-error-message">

          <span className="profile-message-icon">
            !
          </span>

          <span>
            {error}
          </span>

        </div>
      )}


      {/* =====================================================
          PROFILE OVERVIEW
      ===================================================== */}

      <section className="profile-overview">

        <div className="profile-overview-main">

          <div className="profile-avatar">

            {hasProfileImage ? (
              <img
                src={imagePreview}
                alt={displayName}
              />
            ) : (
              avatarLetter
            )}

          </div>

          <div className="profile-overview-info">

            <div className="profile-name-row">

              <h2>
                {displayName}
              </h2>

              <span className="profile-status-badge">
                Profile
              </span>

            </div>

            <p className="profile-goal">
              {displayGoal}
            </p>

            {profile.location && (
              <span className="profile-location">

                <span>
                  ⌖
                </span>

                {profile.location}

              </span>
            )}

            {account.email && (
              <span className="profile-location">

                <span>
                  ✉
                </span>

                {account.email}

              </span>
            )}

            {profile.linkedin_url && (
              <a
                className="profile-link"
                href={
                  profile.linkedin_url
                }
                target="_blank"
                rel="noreferrer"
              >
                LinkedIn Profile ↗
              </a>
            )}

          </div>

        </div>


        <div className="profile-overview-stats">

          <div>

            <span>
              Profile
            </span>

            <strong>
              {profileCompleteness}%
            </strong>

          </div>

          <div>

            <span>
              Projects
            </span>

            <strong>
              {totalProjects}
            </strong>

          </div>

          <div>

            <span>
              Completed
            </span>

            <strong>
              {completedProjects.length}
            </strong>

          </div>

        </div>

      </section>


      {/* =====================================================
          COMPLETENESS
      ===================================================== */}

      <section className="profile-completeness-card">

        <div className="profile-completeness-left">

          <div className="profile-progress-ring">

            <div
              className="profile-progress-ring-fill"
              style={{
                "--profile-progress":
                  profileCompleteness,
              }}
            >

              <div className="profile-progress-ring-inner">

                <strong>
                  {profileCompleteness}
                </strong>

                <span>
                  %
                </span>

              </div>

            </div>

          </div>

          <div>

            <span className="profile-eyebrow">
              PROFILE STRENGTH
            </span>

            <h2>
              {profileStrengthLabel}
            </h2>

            <p>
              {profileStrengthDescription}
            </p>

          </div>

        </div>


        <div className="profile-completeness-right">

          <div className="profile-completeness-heading">

            <span>
              Profile completeness
            </span>

            <strong>
              {completedFields}/
              {profileFields.length}
            </strong>

          </div>

          <div className="profile-progress-bar">

            <div
              style={{
                width: `${profileCompleteness}%`,
              }}
            />

          </div>

          {remainingFields.length > 0 ? (

            <div className="profile-missing-fields">

              <span>
                Still missing:
              </span>

              {remainingFields
                .slice(0, 3)
                .map(
                  (field) => (
                    <span
                      className="profile-missing-pill"
                      key={field.label}
                    >
                      {field.label}
                    </span>
                  )
                )}

              {remainingFields.length >
                3 && (
                <span className="profile-missing-more">
                  +{remainingFields.length - 3} more
                </span>
              )}

            </div>

          ) : (

            <div className="profile-complete-message">
              ✓ All profile essentials are complete.
            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          PROFILE LAYOUT
      ===================================================== */}

      <div className="profile-layout">

        {/* ===================================================
            LEFT: PROFILE CARD
        =================================================== */}

        <aside className="profile-card">

          <div className="profile-card-heading">

            <span className="profile-eyebrow">
              PROFILE PREVIEW
            </span>

            <h3>
              Professional Identity
            </h3>

          </div>


          <div className="profile-card-avatar">

            {hasProfileImage ? (
              <img
                src={imagePreview}
                alt={displayName}
              />
            ) : (
              avatarLetter
            )}

          </div>


          <h3 className="profile-card-name">
            {displayName}
          </h3>


          <p className="profile-card-goal">
            {displayGoal}
          </p>


          {profile.location && (
            <div className="profile-card-location">
              ⌖ {profile.location}
            </div>
          )}


          <div className="profile-divider" />


          <div className="profile-preview-row">

            <span>
              Username
            </span>

            <strong>
              {account.username || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              Email
            </span>

            <strong>
              {account.email || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              Full Name
            </span>

            <strong>
              {profile.full_name || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              Phone
            </span>

            <strong>
              {profile.phone || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              Location
            </span>

            <strong>
              {profile.location || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              Career Goal
            </span>

            <strong>
              {profile.career_goal || "—"}
            </strong>

          </div>


          <div className="profile-preview-row">

            <span>
              LinkedIn
            </span>

            <strong>
              {profile.linkedin_url
                ? "Added"
                : "Not added"}
            </strong>

          </div>


          <div className="profile-card-actions">

            {profile.linkedin_url && (
              <a
                className="profile-link-button"
                href={
                  profile.linkedin_url
                }
                target="_blank"
                rel="noreferrer"
              >
                View LinkedIn ↗
              </a>
            )}

            <button
              type="button"
              className="profile-outline-action"
              onClick={() =>
                navigate("/portfolio")
              }
            >
              View Portfolio →
            </button>

          </div>

        </aside>


        {/* ===================================================
            RIGHT: EDIT FORM
        =================================================== */}

        <section className="profile-form-card">

          <div className="profile-form-heading">

            <div>

              <span className="profile-eyebrow">
                PERSONAL INFORMATION
              </span>

              <h2>
                Tell us about yourself
              </h2>

              <p>
                Your account information is loaded
                automatically. Add professional details
                to improve your recommendations,
                CVs, projects, and job matches.
              </p>

            </div>

            <div className="profile-form-ai-badge">
              AI

              <span>
                Powered Profile
              </span>
            </div>

          </div>


          <form
            className="profile-form"
            onSubmit={handleSubmit}
          >

            {/* =================================================
                PROFILE PHOTO
            ================================================= */}

            <div className="profile-form-section">

              <div className="profile-form-section-title">
                Profile Photo
              </div>

              <div className="profile-photo-editor">

                <div className="profile-photo-editor-preview">

                  {hasProfileImage ? (
                    <img
                      src={imagePreview}
                      alt={displayName}
                    />
                  ) : (
                    <span>
                      {avatarLetter}
                    </span>
                  )}

                </div>

                <div className="profile-photo-editor-content">

                  <div>

                    <strong>
                      Professional Profile Photo
                    </strong>

                    <p>
                      Add a clear professional photo.
                      It will be used across your profile
                      and can also appear on your CV.
                    </p>

                  </div>

                  <div className="profile-photo-actions">

                    <label
                      htmlFor="profile-image-upload"
                      className="profile-photo-upload-button"
                    >
                      {uploadingImage
                        ? "Uploading..."
                        : hasProfileImage
                        ? "Change Photo"
                        : "Upload Photo"}
                    </label>

                    <input
                      id="profile-image-upload"
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleImageChange}
                      disabled={
                        uploadingImage
                      }
                      hidden
                    />

                    <small>
                      JPG, JPEG, PNG, or WEBP · Max 2MB
                    </small>

                  </div>

                </div>

              </div>

            </div>


            {/* =================================================
                ACCOUNT INFORMATION
            ================================================= */}

            <div className="profile-form-section">

              <div className="profile-form-section-title">
                Account Information
              </div>

              <div className="profile-form-grid">

                <div className="profile-form-group">

                  <label htmlFor="profile-username">
                    Username
                  </label>

                  <input
                    id="profile-username"
                    type="text"
                    value={
                      account.username
                    }
                    placeholder="Your username"
                    readOnly
                    disabled
                  />

                  <small>
                    This comes from your account and
                    cannot be changed here.
                  </small>

                </div>


                <div className="profile-form-group">

                  <label htmlFor="profile-email">
                    Email
                  </label>

                  <input
                    id="profile-email"
                    type="email"
                    value={
                      account.email
                    }
                    placeholder="Your email"
                    readOnly
                    disabled
                  />

                  <small>
                    Your account email is loaded automatically.
                  </small>

                </div>

              </div>

            </div>


            {/* =================================================
                BASIC INFORMATION
            ================================================= */}

            <div className="profile-form-section">

              <div className="profile-form-section-title">
                Basic Information
              </div>

              <div className="profile-form-grid">

                <div className="profile-form-group">

                  <label htmlFor="full_name">
                    Full Name
                  </label>

                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    value={
                      profile.full_name
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="Your full name"
                    autoComplete="name"
                  />

                  <small>
                    This is automatically populated
                    when possible, and you can edit it.
                  </small>

                </div>


                <div className="profile-form-group">

                  <label htmlFor="phone">
                    Phone
                  </label>

                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={
                      profile.phone
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="+20..."
                    autoComplete="tel"
                  />

                  <small>
                    Add a professional contact number.
                  </small>

                </div>


                <div className="profile-form-group">

                  <label htmlFor="location">
                    Location
                  </label>

                  <input
                    id="location"
                    name="location"
                    type="text"
                    value={
                      profile.location
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="City, Country"
                    autoComplete="address-level2"
                  />

                  <small>
                    Example: Cairo, Egypt.
                  </small>

                </div>


                <div className="profile-form-group">

                  <label htmlFor="career_goal">
                    Target Career
                  </label>

                  <input
                    id="career_goal"
                    name="career_goal"
                    type="text"
                    value={
                      profile.career_goal
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="Full Stack Developer & AI"
                  />

                  <small>
                    This guides job matching and
                    recommendations.
                  </small>

                </div>

              </div>

            </div>


            {/* =================================================
                PROFESSIONAL BRANDING
            ================================================= */}

            <div className="profile-form-section">

              <div className="profile-form-section-title">
                Professional Branding
              </div>


              <div className="profile-form-group">

                <label htmlFor="linkedin_url">
                  LinkedIn URL
                </label>

                <input
                  id="linkedin_url"
                  name="linkedin_url"
                  type="url"
                  value={
                    profile.linkedin_url
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="https://linkedin.com/in/your-profile"
                  autoComplete="url"
                />

                <small>
                  Your professional profile will be
                  available from your CV and portfolio.
                </small>

              </div>


              <div className="profile-form-group">

                <label htmlFor="bio">
                  Professional About
                </label>

                <textarea
                  id="bio"
                  name="bio"
                  value={profile.bio}
                  onChange={
                    handleChange
                  }
                  placeholder="Tell us about your background, experience, projects, strengths, interests, and the kind of work you want to do..."
                  rows={8}
                />

                <div className="profile-textarea-footer">

                  <small>
                    A strong summary helps the AI
                    personalize your career path.
                  </small>

                  <span>
                    {profile.bio.length}
                    {" "}
                    characters
                  </span>

                </div>

              </div>

            </div>


            {/* =================================================
                FORM ACTIONS
            ================================================= */}

            <div className="profile-actions">

              <button
                type="button"
                className="profile-secondary-button"
                onClick={() =>
                  navigate(
                    "/dashboard"
                  )
                }
                disabled={
                  saving ||
                  uploadingImage
                }
              >
                Cancel
              </button>


              <button
                type="submit"
                className="profile-primary-button"
                disabled={
                  saving ||
                  uploadingImage
                }
              >
                {saving ? (
                  <>
                    <span className="profile-button-spinner" />
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </button>

            </div>

          </form>

        </section>

      </div>


      {/* =====================================================
          ACCOUNT SECURITY
      ===================================================== */}

      <AccountSecurity />


      {/* =====================================================
          CAREER SNAPSHOT
      ===================================================== */}

      <section className="profile-career-section">

        <div className="profile-section-heading">

          <div>

            <span className="profile-eyebrow">
              CAREER SNAPSHOT
            </span>

            <h2>
              Your Career Evidence
            </h2>

            <p>
              Your profile becomes more valuable
              when it is supported by measurable
              practical experience.
            </p>

          </div>

        </div>


        <div className="profile-career-grid">

          <article className="profile-career-stat">

            <span>
              Total Projects
            </span>

            <strong>
              {totalProjects}
            </strong>

            <small>
              Across your career workspace
            </small>

          </article>


          <article className="profile-career-stat">

            <span>
              Completed
            </span>

            <strong>
              {completedProjects.length}
            </strong>

            <small>
              Portfolio-ready projects
            </small>

          </article>


          <article className="profile-career-stat">

            <span>
              In Progress
            </span>

            <strong>
              {activeProjects.length}
            </strong>

            <small>
              Projects currently being built
            </small>

          </article>


          <article className="profile-career-stat">

            <span>
              Portfolio Progress
            </span>

            <strong>
              {projectCompletionRate}%
            </strong>

            <small>
              Completion rate
            </small>

          </article>

        </div>

      </section>


      {/* =====================================================
          PORTFOLIO PREVIEW
      ===================================================== */}

      <section className="portfolio-section">

        <div className="profile-section-heading">

          <div>

            <span className="profile-eyebrow">
              PORTFOLIO
            </span>

            <h2>
              My Career Portfolio
            </h2>

            <p>
              Showcase your completed projects
              and practical experience to employers.
            </p>

          </div>


          <button
            type="button"
            className="profile-text-action"
            onClick={() =>
              navigate("/portfolio")
            }
          >
            Open Full Portfolio →
          </button>

        </div>


        {completedProjects.length === 0 ? (

          <div className="portfolio-empty">

            <div className="portfolio-empty-icon">
              +
            </div>

            <div>

              <h3>
                Start building your portfolio
              </h3>

              <p>
                Complete practical projects to
                create evidence of your skills.
              </p>

            </div>

            <button
              type="button"
              className="profile-secondary-button"
              onClick={() =>
                navigate("/projects")
              }
            >
              Find Projects
            </button>

          </div>

        ) : (

          <div className="portfolio-grid">

            {completedProjects
              .slice(0, 4)
              .map(
                (project) => (
                  <article
                    className="portfolio-card"
                    key={project.id}
                  >

                    <div className="portfolio-card-top">

                      <div>

                        <span className="portfolio-completed">
                          ✓ Completed
                        </span>

                        <h3>
                          {project.title}
                        </h3>

                      </div>

                      {project.difficulty && (
                        <span className="portfolio-difficulty">
                          {project.difficulty}
                        </span>
                      )}

                    </div>


                    <p>
                      {project.description ||
                        "No project description available."}
                    </p>


                    {project.target_role && (
                      <div className="portfolio-target">

                        <span>
                          Target Role
                        </span>

                        <strong>
                          {project.target_role}
                        </strong>

                      </div>
                    )}


                    {Array.isArray(
                      project.skills
                    ) &&
                      project.skills.length > 0 && (
                        <div className="portfolio-card-skills">

                          {project.skills
                            .slice(0, 7)
                            .map(
                              (
                                skill,
                                index
                              ) => (
                                <span
                                  key={`${project.id}-${skill}-${index}`}
                                >
                                  {skill}
                                </span>
                              )
                            )}

                          {project.skills.length >
                            7 && (
                            <span>
                              +
                              {project.skills.length -
                                7}
                            </span>
                          )}

                        </div>
                      )}


                    {Array.isArray(
                      project.objectives
                    ) &&
                      project.objectives.length >
                        0 && (
                        <div className="portfolio-objectives">

                          <strong>
                            Key Outcomes
                          </strong>

                          <ul>
                            {project.objectives
                              .slice(0, 3)
                              .map(
                                (
                                  objective,
                                  index
                                ) => (
                                  <li
                                    key={`${project.id}-objective-${index}`}
                                  >
                                    {objective}
                                  </li>
                                )
                              )}
                          </ul>

                        </div>
                      )}


                    <div className="portfolio-card-links">

                      {project.github_url ? (
                        <a
                          href={
                            project.github_url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          GitHub ↗
                        </a>
                      ) : (
                        <span>
                          GitHub not added
                        </span>
                      )}


                      {project.demo_url ? (
                        <a
                          href={
                            project.demo_url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          Live Demo ↗
                        </a>
                      ) : (
                        <span>
                          Demo not added
                        </span>
                      )}

                    </div>

                  </article>
                )
              )}

          </div>

        )}

        {completedProjects.length > 4 && (
          <div className="portfolio-more">

            <span>
              Showing 4 of{" "}
              {completedProjects.length} completed
              projects
            </span>

            <button
              type="button"
              onClick={() =>
                navigate("/portfolio")
              }
            >
              View All →
            </button>

          </div>
        )}

      </section>


      {/* =====================================================
          CAREER ACTIONS
      ===================================================== */}

      <section className="profile-next-section">

        <div className="profile-section-heading">

          <div>

            <span className="profile-eyebrow">
              NEXT STEPS
            </span>

            <h2>
              Continue Building Your Career
            </h2>

            <p>
              Use the information in your profile
              as the foundation for the rest of
              Career Assistant.
            </p>

          </div>

        </div>


        <div className="profile-next-grid">

          <button
            type="button"
            onClick={() =>
              navigate("/cv")
            }
          >

            <span className="profile-next-icon">
              CV
            </span>

            <span>

              <strong>
                Analyze My CV
              </strong>

              <small>
                Understand the strengths and gaps
                in your current CV.
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

            <span className="profile-next-icon">
              CB
            </span>

            <span>

              <strong>
                Build My CV
              </strong>

              <small>
                Create a professional CV from your
                career data.
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

            <span className="profile-next-icon">
              AI
            </span>

            <span>

              <strong>
                Tailor to a Job
              </strong>

              <small>
                Match your profile with a real
                job opportunity.
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

            <span className="profile-next-icon">
              PJ
            </span>

            <span>

              <strong>
                Build Projects
              </strong>

              <small>
                Turn your skills into portfolio
                evidence.
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

export default Profile;