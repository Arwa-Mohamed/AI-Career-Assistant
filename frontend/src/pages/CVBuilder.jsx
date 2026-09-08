import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getProfile,
  getCVs,
  getCareerProjects,
  analyzeCV,
  analyzeCareerJobMatch,
  sendChatMessage,
} from "../services/api";

import {
  analyzeCVBuilder,
  analyzeCVAgainstJob,
  generateCVPDF,
} from "../services/cvBuilderApi";

import "./CVBuilder.css";

const LOW_VALUE_SKILLS = new Set([
  "http",
  "https",
  "github",
  "git hub",
]);

const SECTION_DEFINITIONS = [
  ["summary", "Professional Summary"],
  ["skills", "Skills"],
  ["experience", "Experience"],
  ["education", "Education"],
  ["certifications", "Certifications"],
  ["projects", "Projects"],
  ["achievements", "Achievements"],
  ["languages", "Languages"],
  ["links", "Professional Links"],
];

const EMPTY_EXPERIENCE = {
  job_title: "",
  company: "",
  duration: "",
  description: "",
};

const EMPTY_EDUCATION = {
  degree: "",
  institution: "",
  year: "",
  description: "",
};

const EMPTY_CERTIFICATION = {
  name: "",
  issuer: "",
  year: "",
};

const EMPTY_PROJECT = {
  title: "",
  target_role: "",
  description: "",
  skills: [],
  objectives: [],
  github_url: "",
  demo_url: "",
};

function cleanString(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  return String(value).trim();
}

function normalizeList(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  return value;
}

function uniqueStrings(values) {
  const result = [];
  const seen = new Set();

  for (const value of values) {
    const text = cleanString(value);

    if (!text) {
      continue;
    }

    const key = text.toLowerCase();

    if (seen.has(key)) {
      continue;
    }

    seen.add(key);
    result.push(text);
  }

  return result;
}

function normalizeObjectList(
  values
) {
  if (!Array.isArray(values)) {
    return [];
  }

  return values.filter(
    (item) =>
      item &&
      typeof item === "object"
  );
}

function getField(
  item,
  keys = [],
  fallback = ""
) {
  if (
    !item ||
    typeof item !== "object"
  ) {
    return fallback;
  }

  for (const key of keys) {
    const value = item[key];

    if (
      value !== null &&
      value !== undefined &&
      cleanString(value)
    ) {
      return value;
    }
  }

  return fallback;
}

function normalizeExperienceItem(
  item
) {
  return {
    job_title: cleanString(
      getField(item, [
        "job_title",
        "title",
        "position",
        "role",
      ])
    ),
    company: cleanString(
      getField(item, [
        "company",
        "organization",
        "employer",
      ])
    ),
    duration: cleanString(
      getField(item, [
        "duration",
        "date",
        "period",
        "year",
      ])
    ),
    description: cleanString(
      getField(item, [
        "description",
        "responsibilities",
        "details",
      ])
    ),
  };
}

function normalizeEducationItem(
  item
) {
  return {
    degree: cleanString(
      getField(item, [
        "degree",
        "title",
        "program",
        "qualification",
      ])
    ),
    institution: cleanString(
      getField(item, [
        "institution",
        "university",
        "school",
        "college",
      ])
    ),
    year: cleanString(
      getField(item, [
        "year",
        "date",
        "period",
      ])
    ),
    description: cleanString(
      getField(item, [
        "description",
        "details",
      ])
    ),
  };
}

function normalizeCertificationItem(
  item
) {
  if (typeof item === "string") {
    return {
      name: cleanString(item),
      issuer: "",
      year: "",
    };
  }

  return {
    name: cleanString(
      getField(item, [
        "name",
        "title",
        "certificate",
        "certification",
      ])
    ),
    issuer: cleanString(
      getField(item, [
        "issuer",
        "organization",
        "provider",
        "institution",
      ])
    ),
    year: cleanString(
      getField(item, [
        "year",
        "date",
        "period",
      ])
    ),
  };
}

function normalizeProjectItem(
  item
) {
  return {
    title: cleanString(
      getField(item, [
        "title",
        "name",
      ])
    ),
    target_role: cleanString(
      getField(item, [
        "target_role",
        "role",
      ])
    ),
    description: cleanString(
      getField(item, [
        "description",
      ])
    ),
    skills: uniqueStrings(
      normalizeList(
        getField(item, [
          "skills",
          "technologies",
          "tech_stack",
        ], [])
      )
    ),
    objectives: uniqueStrings(
      normalizeList(
        getField(item, [
          "objectives",
          "outcomes",
          "highlights",
        ], [])
      )
    ),
    github_url: cleanString(
      getField(item, [
        "github_url",
        "github",
      ])
    ),
    demo_url: cleanString(
      getField(item, [
        "demo_url",
        "demo",
        "live_url",
      ])
    ),
  };
}

function getAssistantText(
  response
) {
  if (
    typeof response === "string"
  ) {
    return response.trim();
  }

  if (
    !response ||
    typeof response !== "object"
  ) {
    return "";
  }

  const directKeys = [
    "reply",
    "response",
    "message",
    "content",
    "text",
    "answer",
  ];

  for (const key of directKeys) {
    if (
      typeof response[key] ===
      "string"
    ) {
      const value =
        response[key].trim();

      if (value) {
        return value;
      }
    }
  }

  const nestedKeys = [
    "data",
    "result",
    "assistant",
  ];

  for (const key of nestedKeys) {
    const value =
      getAssistantText(
        response[key]
      );

    if (value) {
      return value;
    }
  }

  return "";
}

function buildFallbackSummary(
  title,
  skills
) {
  const role =
    cleanString(title) ||
    "professional";

  const selectedSkills =
    skills
      .slice(0, 6)
      .join(", ");

  if (selectedSkills) {
    return (
      `${role} with practical experience in ${selectedSkills}. ` +
      "Focused on building reliable, results-oriented solutions and continuously developing professional capabilities."
    );
  }

  return (
    `${role} focused on building practical, high-quality solutions and continuously developing professional skills.`
  );
}

function isInternshipLike(text) {
  const value =
    cleanString(text).toLowerCase();

  return (
    value.includes("intern") ||
    value.includes("internship") ||
    value.includes("trainee") ||
    value.includes("placement")
  );
}

function looksLikeCertification(
  text
) {
  const value =
    cleanString(text).toLowerCase();

  return (
    value.includes("course") ||
    value.includes("certificate") ||
    value.includes("certification") ||
    value.includes("training") ||
    value.includes("program") ||
    value.includes("academy") ||
    value.includes("maharatech") ||
    value.includes("udemy") ||
    value.includes("coursera")
  );
}

function extractFallbackCertifications(
  extractedText
) {
  const text =
    cleanString(extractedText);

  if (!text) {
    return [];
  }

  const lines =
    text
      .split(/\r?\n/)
      .map((line) =>
        cleanString(
          line.replace(
            /^[•▪●◦*-]\s*/,
            ""
          )
        )
      )
      .filter(Boolean);

  const results = [];

  for (const line of lines) {
    if (
      isInternshipLike(line)
    ) {
      continue;
    }

    if (
      looksLikeCertification(
        line
      )
    ) {
      results.push({
        name: line,
        issuer: "",
        year: "",
      });
    }
  }

  return results;
}

function CVBuilder() {
  const [profile, setProfile] =
    useState(null);

  const [cvs, setCVs] =
    useState([]);

  const [projects, setProjects] =
    useState([]);

  const [selectedCV, setSelectedCV] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [generatingPDF, setGeneratingPDF] =
    useState(false);

  const [analyzingATS, setAnalyzingATS] =
    useState(false);

  const [analyzingJob, setAnalyzingJob] =
    useState(false);

  const [aiBusy, setAIBusy] =
    useState("");

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [template, setTemplate] =
    useState("modern");

  const [jobDescription, setJobDescription] =
    useState("");

  const [jobAnalysis, setJobAnalysis] =
    useState(null);

  const [atsResult, setATSResult] =
    useState(null);

  const [sections, setSections] =
    useState({
      summary: true,
      skills: true,
      experience: true,
      education: true,
      certifications: true,
      projects: true,
      achievements: true,
      languages: true,
      links: true,
    });

  const [cvInfo, setCvInfo] =
    useState({
      name: "",
      title: "",
      email: "",
      phone: "",
      location: "",
      linkedin: "",
      github: "",
      portfolio: "",
      summary: "",
    });

  const [skillList, setSkillList] =
    useState([]);

  const [experience, setExperience] =
    useState([]);

  const [education, setEducation] =
    useState([]);

  const [certifications, setCertifications] =
    useState([]);

  const [cvProjects, setCVProjects] =
    useState([]);

  const [achievements, setAchievements] =
    useState([]);

  const [languages, setLanguages] =
    useState([]);

  const [activePanel, setActivePanel] =
    useState("personal");

  // =========================================================
  // LOAD DATA
  // =========================================================

  useEffect(() => {
    let mounted = true;

    const loadData =
      async () => {
        try {
          setLoading(true);
          setError("");

          const [
            profileData,
            cvsData,
            projectsData,
          ] = await Promise.all([
            getProfile(),
            getCVs(),
            getCareerProjects(),
          ]);

          if (!mounted) {
            return;
          }

          const normalizedProfile =
            profileData || {};

          const normalizedCVs =
            Array.isArray(cvsData)
              ? cvsData
              : [];

          const normalizedProjects =
            Array.isArray(projectsData)
              ? projectsData
              : [];

          setProfile(
            normalizedProfile
          );

          setCVs(
            normalizedCVs
          );

          setProjects(
            normalizedProjects
          );

          const profileName =
            normalizedProfile.full_name ||
            normalizedProfile.name ||
            "";

          const careerGoal =
            normalizedProfile.career_goal ||
            "Software Developer";

          setCvInfo({
            name:
              profileName,

            title:
              careerGoal,

            email:
              normalizedProfile.email ||
              "",

            phone:
              normalizedProfile.phone ||
              "",

            location:
              normalizedProfile.location ||
              "",

            linkedin:
              normalizedProfile.linkedin_url ||
              "",

            github:
              normalizedProfile.github_url ||
              "",

            portfolio:
              normalizedProfile.portfolio_url ||
              "",

            summary:
              normalizedProfile.bio ||
              "",
          });

          if (
            normalizedCVs.length > 0
          ) {
            setSelectedCV(
              String(
                normalizedCVs[0].id
              )
            );
          }
        } catch (err) {
          if (!mounted) {
            return;
          }

          setError(
            err?.message ||
              "Failed to load your career data."
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
  // SELECTED CV
  // =========================================================

  const selectedCVData =
    useMemo(() => {
      return cvs.find(
        (cv) =>
          String(cv.id) ===
          String(selectedCV)
      );
    }, [
      cvs,
      selectedCV,
    ]);

  const parsedData =
    selectedCVData?.parsed_data || {};

  const extractedText =
    selectedCVData?.extracted_text ||
    "";

  // =========================================================
  // COMPLETED PROJECTS
  // =========================================================

  const completedProjects =
    useMemo(() => {
      return projects.filter(
        (project) =>
          project?.status ===
          "completed"
      );
    }, [projects]);

  // =========================================================
  // BUILD EDITOR DATA FROM SOURCE CV
  // =========================================================

  useEffect(() => {
    if (!selectedCVData) {
      return;
    }

    const rawSkills = [
      ...normalizeList(
        parsedData.skills
      ),
      ...normalizeList(
        parsedData.technical_skills
      ),
    ];

    completedProjects.forEach(
      (project) => {
        rawSkills.push(
          ...normalizeList(
            project?.skills
          )
        );
      }
    );

    const cleanedSkills =
      uniqueStrings(
        rawSkills
      ).filter(
        (skill) =>
          !LOW_VALUE_SKILLS.has(
            skill.toLowerCase()
          )
      );

    setSkillList(
      cleanedSkills
    );

    const parsedExperience =
      normalizeObjectList(
        parsedData.experience
      ).map(
        normalizeExperienceItem
      );

    setExperience(
      parsedExperience
    );

    const parsedEducation =
      normalizeObjectList(
        parsedData.education
      ).map(
        normalizeEducationItem
      );

    setEducation(
      parsedEducation
    );

    let parsedCertificates =
      normalizeList(
        parsedData.certifications
      ).map(
        normalizeCertificationItem
      );

    const parsedTraining =
      normalizeList(
        parsedData.training
      ).map(
        normalizeCertificationItem
      );

    parsedCertificates = [
      ...parsedCertificates,
      ...parsedTraining,
    ];

    if (
      parsedCertificates.length ===
      0
    ) {
      parsedCertificates =
        extractFallbackCertifications(
          extractedText
        );
    }

    const certificateMap =
      new Map();

    [
      ...parsedCertificates,
    ].forEach(
      (certificate) => {
        if (
          !certificate ||
          !certificate.name ||
          isInternshipLike(
            certificate.name
          )
        ) {
          return;
        }

        const key =
          certificate.name.toLowerCase();

        if (
          !certificateMap.has(key)
        ) {
          certificateMap.set(
            key,
            certificate
          );
        }
      }
    );

    setCertifications(
      Array.from(
        certificateMap.values()
      )
    );

    const parsedCVProjects =
      normalizeObjectList(
        parsedData.projects
      ).map(
        normalizeProjectItem
      );

    const careerProjects =
      completedProjects.map(
        normalizeProjectItem
      );

    const projectMap =
      new Map();

    [
      ...parsedCVProjects,
      ...careerProjects,
    ].forEach(
      (project) => {
        if (
          !project.title
        ) {
          return;
        }

        const key =
          project.title.toLowerCase();

        if (
          !projectMap.has(key)
        ) {
          projectMap.set(
            key,
            project
          );
        }
      }
    );

    setCVProjects(
      Array.from(
        projectMap.values()
      )
    );

    const parsedAchievements =
      uniqueStrings(
        normalizeList(
          parsedData.achievements
        )
      );

    setAchievements(
      parsedAchievements
    );

    const parsedLanguages =
      uniqueStrings(
        normalizeList(
          parsedData.languages
        )
      );

    setLanguages(
      parsedLanguages
    );

    const parsedSummary =
      cleanString(
        parsedData.summary ||
          parsedData.profile ||
          parsedData.objective
      );

    const nextTitle =
      cleanString(
        parsedData.title ||
          cvInfo.title
      );

    setCvInfo(
      (previous) => ({
        ...previous,
        title:
          nextTitle ||
          previous.title,
        summary:
          previous.summary ||
          parsedSummary ||
          buildFallbackSummary(
            previous.title,
            cleanedSkills
          ),
      })
    );
  }, [
    selectedCVData,
    completedProjects,
  ]);

  // =========================================================
  // INPUT HANDLERS
  // =========================================================

  const clearAlerts =
    () => {
      setError("");
      setMessage("");
    };

  const handleInfoChange =
    (
      field,
      value
    ) => {
      setCvInfo(
        (previous) => ({
          ...previous,
          [field]: value,
        })
      );

      clearAlerts();
    };

  const toggleSection =
    (section) => {
      setSections(
        (previous) => ({
          ...previous,
          [section]:
            !previous[section],
        })
      );
    };

  const enableAllSections =
    () => {
      setSections({
        summary: true,
        skills: true,
        experience: true,
        education: true,
        certifications: true,
        projects: true,
        achievements: true,
        languages: true,
        links: true,
      });
    };

  const disableAllSections =
    () => {
      setSections({
        summary: false,
        skills: false,
        experience: false,
        education: false,
        certifications: false,
        projects: false,
        achievements: false,
        languages: false,
        links: false,
      });
    };

  // =========================================================
  // ARRAY EDITORS
  // =========================================================

  const updateExperience =
    (
      index,
      field,
      value
    ) => {
      setExperience(
        (previous) =>
          previous.map(
            (item, itemIndex) =>
              itemIndex === index
                ? {
                    ...item,
                    [field]:
                      value,
                  }
                : item
          )
      );
    };

  const addExperience =
    () => {
      setExperience(
        (previous) => [
          ...previous,
          {
            ...EMPTY_EXPERIENCE,
          },
        ]
      );
    };

  const removeExperience =
    (index) => {
      setExperience(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  const updateEducation =
    (
      index,
      field,
      value
    ) => {
      setEducation(
        (previous) =>
          previous.map(
            (item, itemIndex) =>
              itemIndex === index
                ? {
                    ...item,
                    [field]:
                      value,
                  }
                : item
          )
      );
    };

  const addEducation =
    () => {
      setEducation(
        (previous) => [
          ...previous,
          {
            ...EMPTY_EDUCATION,
          },
        ]
      );
    };

  const removeEducation =
    (index) => {
      setEducation(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  const updateCertification =
    (
      index,
      field,
      value
    ) => {
      setCertifications(
        (previous) =>
          previous.map(
            (item, itemIndex) =>
              itemIndex === index
                ? {
                    ...item,
                    [field]:
                      value,
                  }
                : item
          )
      );
    };

  const addCertification =
    () => {
      setCertifications(
        (previous) => [
          ...previous,
          {
            ...EMPTY_CERTIFICATION,
          },
        ]
      );
    };

  const removeCertification =
    (index) => {
      setCertifications(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  const updateProject =
    (
      index,
      field,
      value
    ) => {
      setCVProjects(
        (previous) =>
          previous.map(
            (item, itemIndex) =>
              itemIndex === index
                ? {
                    ...item,
                    [field]:
                      value,
                  }
                : item
          )
      );
    };

  const updateProjectArrayField =
    (
      index,
      field,
      value
    ) => {
      setCVProjects(
        (previous) =>
          previous.map(
            (item, itemIndex) =>
              itemIndex === index
                ? {
                    ...item,
                    [field]:
                      value
                        .split(",")
                        .map(
                          (valueItem) =>
                            valueItem.trim()
                        )
                        .filter(Boolean),
                  }
                : item
          )
      );
    };

  const addProject =
    () => {
      setCVProjects(
        (previous) => [
          ...previous,
          {
            ...EMPTY_PROJECT,
          },
        ]
      );
    };

  const removeProject =
    (index) => {
      setCVProjects(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  const addSkill =
    () => {
      setSkillList(
        (previous) => [
          ...previous,
          "New Skill",
        ]
      );
    };

  const updateSkill =
    (index, value) => {
      setSkillList(
        (previous) =>
          previous.map(
            (skill, skillIndex) =>
              skillIndex === index
                ? value
                : skill
          )
      );
    };

  const removeSkill =
    (index) => {
      setSkillList(
        (previous) =>
          previous.filter(
            (_, skillIndex) =>
              skillIndex !== index
          )
      );
    };

  const addAchievement =
    () => {
      setAchievements(
        (previous) => [
          ...previous,
          "",
        ]
      );
    };

  const updateAchievement =
    (
      index,
      value
    ) => {
      setAchievements(
        (previous) =>
          previous.map(
            (
              item,
              itemIndex
            ) =>
              itemIndex === index
                ? value
                : item
          )
      );
    };

  const removeAchievement =
    (index) => {
      setAchievements(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  const addLanguage =
    () => {
      setLanguages(
        (previous) => [
          ...previous,
          "",
        ]
      );
    };

  const updateLanguage =
    (
      index,
      value
    ) => {
      setLanguages(
        (previous) =>
          previous.map(
            (
              item,
              itemIndex
            ) =>
              itemIndex === index
                ? value
                : item
          )
      );
    };

  const removeLanguage =
    (index) => {
      setLanguages(
        (previous) =>
          previous.filter(
            (_, itemIndex) =>
              itemIndex !== index
          )
      );
    };

  // =========================================================
  // AI SUMMARY
  // =========================================================

  const handleAISummary =
    async () => {
      try {
        setAIBusy("summary");
        clearAlerts();

        const jobContext =
          jobDescription.trim()
            ? `
Target Job Description:
${jobDescription.trim()}
`
            : "";

        const prompt = `
You are an expert professional CV writer.

Rewrite the candidate's Professional Summary for a modern ATS-friendly CV.

Rules:
- Use ONLY information explicitly present below.
- Do not invent years of experience.
- Do not invent employers.
- Do not invent achievements, metrics, technologies, or certifications.
- Keep it between 45 and 85 words.
- Make it specific to the target role.
- Use strong but truthful professional language.
- Avoid first-person wording.
- Return ONLY the final summary paragraph.

Candidate:
Name: ${cvInfo.name}
Target Role: ${cvInfo.title}

Skills:
${skillList.join(", ")}

Experience:
${JSON.stringify(
  experience
)}

Education:
${JSON.stringify(
  education
)}

Projects:
${JSON.stringify(
  cvProjects
)}

Certifications:
${JSON.stringify(
  certifications
)}

${jobContext}
`;

        let response;

        try {
          response =
            await sendChatMessage(
              prompt
            );
        } catch {
          response =
            await sendChatMessage(
              prompt,
              null
            );
        }

        const generated =
          getAssistantText(
            response
          );

        if (!generated) {
          throw new Error(
            "The AI assistant did not return a usable summary."
          );
        }

        setCvInfo(
          (previous) => ({
            ...previous,
            summary:
              generated
                .replace(/^["']/, "")
                .replace(/["']$/, "")
                .trim(),
          })
        );

        setMessage(
          "AI generated a stronger professional summary."
        );
      } catch (err) {
        setError(
          err?.message ||
            "Failed to improve the professional summary."
        );
      } finally {
        setAIBusy("");
      }
    };

  // =========================================================
  // ATS ANALYSIS
  // =========================================================

  const handleATSAnalysis =
    async () => {
      if (!selectedCV) {
        setError(
          "Please select a source CV first."
        );
        return;
      }

      try {
        setAnalyzingATS(true);
        clearAlerts();

        let result;

        try {
          result =
            await analyzeCVBuilder(
              Number(selectedCV)
            );
        } catch {
          result =
            await analyzeCV(
              Number(selectedCV)
            );
        }

        setATSResult(
          result?.ats ||
            result?.breakdown?.ats ||
            null
        );

        setMessage(
          "ATS analysis updated."
        );
      } catch (err) {
        setError(
          err?.message ||
            "Failed to analyze the source CV."
        );
      } finally {
        setAnalyzingATS(false);
      }
    };

  // =========================================================
  // JOB MATCH
  // =========================================================

  const handleJobAnalysis =
    async () => {
      if (!selectedCV) {
        setError(
          "Please select a source CV first."
        );
        return;
      }

      if (
        !jobDescription.trim()
      ) {
        setError(
          "Paste a job description first."
        );
        return;
      }

      try {
        setAnalyzingJob(true);
        clearAlerts();

        let result;

        try {
          result =
            await analyzeCVAgainstJob(
              Number(selectedCV),
              jobDescription
            );
        } catch {
          result =
            await analyzeCareerJobMatch(
              Number(selectedCV),
              jobDescription
            );
        }

        setJobAnalysis(
          result
        );

        setMessage(
          "Job-specific CV alignment calculated successfully."
        );
      } catch (err) {
        setError(
          err?.message ||
            "Failed to analyze the job description."
        );
      } finally {
        setAnalyzingJob(false);
      }
    };

  // =========================================================
  // PAYLOAD
  // =========================================================

  const buildPDFPayload =
    () => {
      return {
        name:
          cvInfo.name,
        title:
          cvInfo.title,
        email:
          cvInfo.email,
        phone:
          cvInfo.phone,
        location:
          cvInfo.location,
        linkedin:
          cvInfo.linkedin,
        github:
          cvInfo.github,
        portfolio:
          cvInfo.portfolio,
        summary:
          cvInfo.summary,

        cv_id:
          selectedCV
            ? Number(selectedCV)
            : null,

        template,

        sections,

        content: {
          skills:
            skillList
              .map(cleanString)
              .filter(Boolean),

          experience:
            experience.map(
              normalizeExperienceItem
            ),

          education:
            education.map(
              normalizeEducationItem
            ),

          certifications:
            certifications
              .map(
                normalizeCertificationItem
              )
              .filter(
                (item) =>
                  item.name
              ),

          projects:
            cvProjects.map(
              normalizeProjectItem
            ),

          achievements:
            uniqueStrings(
              achievements
            ),

          languages:
            uniqueStrings(
              languages
            ),

          links: {
            linkedin:
              cvInfo.linkedin,
            github:
              cvInfo.github,
            portfolio:
              cvInfo.portfolio,
          },
        },

        job_target: {
          description:
            jobDescription.trim(),

          analysis:
            jobAnalysis || null,
        },
      };
    };

  // =========================================================
  // GENERATE PDF
  // =========================================================

  const handleGeneratePDF =
    async () => {
      try {
        setGeneratingPDF(true);
        clearAlerts();

        await generateCVPDF(
          buildPDFPayload()
        );

        setMessage(
          "Your professional CV PDF has been generated successfully."
        );
      } catch (err) {
        setError(
          err?.message ||
            "Failed to generate the CV PDF."
        );
      } finally {
        setGeneratingPDF(false);
      }
    };

  // =========================================================
  // PRINT
  // =========================================================

  const handlePrint =
    () => {
      window.print();
    };

  // =========================================================
  // READINESS
  // =========================================================

  const cvReadiness =
    useMemo(() => {
      let score = 0;

      if (
        cvInfo.name.trim()
      ) {
        score += 12;
      }

      if (
        cvInfo.title.trim()
      ) {
        score += 10;
      }

      if (
        cvInfo.email.trim()
      ) {
        score += 10;
      }

      if (
        cvInfo.phone.trim()
      ) {
        score += 8;
      }

      if (
        cvInfo.summary.trim()
      ) {
        score += 15;
      }

      if (
        skillList.length >= 5
      ) {
        score += 15;
      } else if (
        skillList.length > 0
      ) {
        score += 8;
      }

      if (
        experience.length > 0
      ) {
        score += 10;
      }

      if (
        education.length > 0
      ) {
        score += 8;
      }

      if (
        cvProjects.length > 0
      ) {
        score += 8;
      }

      if (
        certifications.length > 0 ||
        achievements.length > 0 ||
        languages.length > 0
      ) {
        score += 4;
      }

      return Math.min(
        score,
        100
      );
    }, [
      cvInfo,
      skillList,
      experience,
      education,
      cvProjects,
      certifications,
      achievements,
      languages,
    ]);

  const cvReadinessLabel =
    cvReadiness >= 90
      ? "Excellent"
      : cvReadiness >= 75
      ? "Strong"
      : cvReadiness >= 55
      ? "Developing"
      : "Needs Work";

  const activeSectionsCount =
    Object.values(
      sections
    ).filter(Boolean).length;

  const dataStatus = [
    {
      label: "Personal Info",
      complete:
        Boolean(
          cvInfo.name &&
            cvInfo.email &&
            cvInfo.phone
        ),
    },
    {
      label: "Professional Summary",
      complete:
        Boolean(
          cvInfo.summary
        ),
    },
    {
      label: "Skills",
      complete:
        skillList.length >= 5,
    },
    {
      label: "Experience",
      complete:
        experience.length > 0,
    },
    {
      label: "Education",
      complete:
        education.length > 0,
    },
    {
      label: "Certifications",
      complete:
        certifications.length > 0,
    },
    {
      label: "Projects",
      complete:
        cvProjects.length > 0,
    },
    {
      label: "Languages",
      complete:
        languages.length > 0,
    },
  ];

  const jobSkills =
    jobAnalysis?.job_skills ||
    jobAnalysis?.analysis?.job_skills ||
    [];

  const matchedSkills =
    jobAnalysis?.matched_skills ||
    jobAnalysis?.analysis?.matched_skills ||
    [];

  const missingSkills =
    jobAnalysis?.missing_skills ||
    jobAnalysis?.analysis?.missing_skills ||
    [];

  const matchScore =
    Number(
      jobAnalysis?.match_percentage ??
        jobAnalysis?.match_score ??
        jobAnalysis?.analysis?.match_percentage ??
        0
    );

  // =========================================================
  // RENDER HELPERS
  // =========================================================

  const renderEditorSection =
    (
      key,
      label,
      children
    ) => {
      const enabled =
        Boolean(
          sections[key]
        );

      return (
        <div
          className={`builder-edit-section ${
            activePanel === key
              ? "active"
              : ""
          }`}
        >
          <button
            type="button"
            className="builder-edit-section-header"
            onClick={() =>
              setActivePanel(
                activePanel === key
                  ? ""
                  : key
              )
            }
          >
            <span>
              {label}
            </span>

            <span>
              {enabled
                ? "Visible"
                : "Hidden"}
            </span>
          </button>

          {activePanel === key && (
            <div className="builder-edit-section-body">
              {children}
            </div>
          )}
        </div>
      );
    };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="cv-builder-page">
        <div className="cv-builder-loading">
          <div className="cv-loader" />

          <div>
            <h2>
              Building your CV workspace...
            </h2>

            <p>
              Loading your profile, source CV,
              career projects and professional data.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="cv-builder-page">
      <header className="builder-header">
        <div className="builder-header-content">
          <div>
            <span className="builder-kicker">
              CAREER TOOLS
            </span>

            <h1>
              AI CV Builder
            </h1>

            <p>
              Build a professional,
              ATS-friendly CV from your
              existing career data, optimize
              it for a target job, and export
              it as a polished PDF.
            </p>
          </div>

          <div className="builder-header-actions">
            <button
              type="button"
              className="builder-secondary-button"
              onClick={handlePrint}
            >
              Print Preview
            </button>

            <button
              type="button"
              className="builder-secondary-button"
              onClick={
                handleATSAnalysis
              }
              disabled={
                analyzingATS
              }
            >
              {analyzingATS
                ? "Analyzing..."
                : "Check ATS"}
            </button>

            <button
              type="button"
              className="generate-button"
              onClick={
                handleGeneratePDF
              }
              disabled={
                generatingPDF
              }
            >
              {generatingPDF
                ? "Generating..."
                : "Generate PDF"}
            </button>
          </div>
        </div>
      </header>

      {message && (
        <div className="cv-builder-success">
          <span>
            ✓
          </span>

          <div>
            <strong>
              Done
            </strong>

            <p>
              {message}
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="cv-builder-inline-error">
          <span>
            !
          </span>

          <div>
            <strong>
              Something went wrong
            </strong>

            <p>
              {error}
            </p>
          </div>
        </div>
      )}

      <section className="builder-overview">
        <div className="builder-readiness">
          <div
            className="builder-readiness-ring"
            style={{
              "--cv-readiness":
                cvReadiness,
            }}
          >
            <div>
              <strong>
                {cvReadiness}
              </strong>

              <span>
                %
              </span>
            </div>
          </div>

          <div>
            <span className="overview-label">
              CV READINESS
            </span>

            <h2>
              {cvReadinessLabel}
            </h2>

            <p>
              Your builder currently has
              {` `}
              {cvReadiness}%
              {` `}
              of the information needed
              for a strong professional CV.
            </p>

            {atsResult?.score !==
              undefined && (
              <div className="overview-mini-metric">
                Source ATS Score:
                <strong>
                  {Math.round(
                    Number(
                      atsResult.score
                    ) || 0
                  )}
                  %
                </strong>
              </div>
            )}
          </div>
        </div>

        <div className="builder-overview-stats">
          <div>
            <span>
              Skills
            </span>

            <strong>
              {skillList.length}
            </strong>
          </div>

          <div>
            <span>
              Experience
            </span>

            <strong>
              {experience.length}
            </strong>
          </div>

          <div>
            <span>
              Education
            </span>

            <strong>
              {education.length}
            </strong>
          </div>

          <div>
            <span>
              Projects
            </span>

            <strong>
              {cvProjects.length}
            </strong>
          </div>
        </div>
      </section>

      <div className="builder-layout">
        <aside className="builder-panel">
          <div className="panel-section">
            <div className="panel-section-heading">
              <div>
                <span>
                  SOURCE
                </span>

                <h3>
                  Career Data
                </h3>
              </div>

              <span className="panel-count">
                {cvs.length}
              </span>
            </div>

            {cvs.length > 0 ? (
              <select
                value={selectedCV}
                onChange={(event) =>
                  setSelectedCV(
                    event.target.value
                  )
                }
                className="builder-select"
              >
                {cvs.map(
                  (cv) => (
                    <option
                      key={cv.id}
                      value={cv.id}
                    >
                      {cv.title ||
                        "My CV"}
                    </option>
                  )
                )}
              </select>
            ) : (
              <div className="empty-source">
                <strong>
                  No uploaded CV
                </strong>

                <span>
                  Upload a CV from My CV first.
                </span>
              </div>
            )}
          </div>

          <div className="panel-section builder-ai-panel">
            <div className="panel-section-heading">
              <div>
                <span>
                  AI ASSISTANT
                </span>

                <h3>
                  Optimize Your CV
                </h3>
              </div>

              <span className="ai-badge">
                AI
              </span>
            </div>

            <p className="panel-help">
              Use the existing AI assistant to
              improve wording while keeping your
              information factual.
            </p>

            <button
              type="button"
              className="ai-action-button"
              onClick={
                handleAISummary
              }
              disabled={
                aiBusy ===
                "summary"
              }
            >
              {aiBusy ===
              "summary"
                ? "AI is writing..."
                : "Improve Professional Summary"}
            </button>
          </div>

          <div className="panel-section">
            <div className="panel-section-heading">
              <div>
                <span>
                  TARGET JOB
                </span>

                <h3>
                  Job-Specific CV
                </h3>
              </div>
            </div>

            <textarea
              className="builder-job-description"
              value={
                jobDescription
              }
              onChange={(event) =>
                setJobDescription(
                  event.target.value
                )
              }
              placeholder="Paste the job description here to align your CV with the role..."
            />

            <button
              type="button"
              className="job-analysis-button"
              onClick={
                handleJobAnalysis
              }
              disabled={
                analyzingJob
              }
            >
              {analyzingJob
                ? "Analyzing Job..."
                : "Analyze Job Match"}
            </button>

            {jobAnalysis && (
              <div className="job-analysis-card">
                <div className="job-score-row">
                  <div>
                    <span>
                      Match
                    </span>

                    <strong>
                      {matchScore.toFixed(
                        0
                      )}
                      %
                    </strong>
                  </div>

                  <div>
                    <span>
                      Job Skills
                    </span>

                    <strong>
                      {jobSkills.length}
                    </strong>
                  </div>
                </div>

                <div className="job-analysis-groups">
                  <div>
                    <span>
                      Matched
                    </span>

                    <strong>
                      {matchedSkills.length}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Missing
                    </span>

                    <strong>
                      {missingSkills.length}
                    </strong>
                  </div>
                </div>

                {missingSkills.length >
                  0 && (
                  <div className="job-missing-skills">
                    <span>
                      Priority gaps
                    </span>

                    <div>
                      {missingSkills
                        .slice(0, 6)
                        .map(
                          (
                            skill,
                            index
                          ) => (
                            <span
                              key={`${skill}-${index}`}
                            >
                              {typeof skill ===
                              "string"
                                ? skill
                                : skill?.name ||
                                  skill?.skill ||
                                  "Skill"}
                            </span>
                          )
                        )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="panel-section">
            <div className="panel-section-heading">
              <div>
                <span>
                  DESIGN
                </span>

                <h3>
                  CV Template
                </h3>
              </div>
            </div>

            <select
              className="builder-select"
              value={template}
              onChange={(event) =>
                setTemplate(
                  event.target.value
                )
              }
            >
              <option value="modern">
                Modern Professional
              </option>

              <option value="ats">
                ATS Classic
              </option>

              <option value="executive">
                Executive
              </option>

              <option value="minimal">
                Minimal
              </option>
            </select>
          </div>

          <div className="panel-section">
            <div className="panel-section-heading">
              <div>
                <span>
                  PERSONAL
                </span>

                <h3>
                  Contact & Summary
                </h3>
              </div>
            </div>

            <div className="builder-fields">
              <label>
                Full Name

                <input
                  type="text"
                  value={
                    cvInfo.name
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "name",
                      event.target.value
                    )
                  }
                  placeholder="Your full name"
                />
              </label>

              <label>
                Professional Title

                <input
                  type="text"
                  value={
                    cvInfo.title
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "title",
                      event.target.value
                    )
                  }
                  placeholder="e.g. Data Analyst"
                />
              </label>

              <label>
                Email

                <input
                  type="email"
                  value={
                    cvInfo.email
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "email",
                      event.target.value
                    )
                  }
                  placeholder="name@example.com"
                />
              </label>

              <label>
                Phone

                <input
                  type="text"
                  value={
                    cvInfo.phone
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "phone",
                      event.target.value
                    )
                  }
                  placeholder="+20..."
                />
              </label>

              <label>
                Location

                <input
                  type="text"
                  value={
                    cvInfo.location
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "location",
                      event.target.value
                    )
                  }
                  placeholder="Assiut, Egypt"
                />
              </label>

              <label>
                LinkedIn

                <input
                  type="text"
                  value={
                    cvInfo.linkedin
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "linkedin",
                      event.target.value
                    )
                  }
                  placeholder="linkedin.com/in/..."
                />
              </label>

              <label>
                GitHub

                <input
                  type="text"
                  value={
                    cvInfo.github
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "github",
                      event.target.value
                    )
                  }
                  placeholder="github.com/..."
                />
              </label>

              <label>
                Portfolio

                <input
                  type="text"
                  value={
                    cvInfo.portfolio
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "portfolio",
                      event.target.value
                    )
                  }
                  placeholder="yourportfolio.com"
                />
              </label>
            </div>
          </div>

          <div className="panel-section builder-content-controls">
            <div className="panel-section-heading">
              <div>
                <span>
                  CONTENT CONTROL
                </span>

                <h3>
                  CV Sections
                </h3>
              </div>

              <span className="panel-count">
                {activeSectionsCount}/9
              </span>
            </div>

            <div className="section-control-actions">
              <button
                type="button"
                onClick={
                  enableAllSections
                }
              >
                Enable All
              </button>

              <button
                type="button"
                onClick={
                  disableAllSections
                }
              >
                Hide All
              </button>
            </div>

            <div className="section-toggle-list">
              {SECTION_DEFINITIONS.map(
                ([key, label]) => (
                  <label
                    className={`section-toggle ${
                      sections[key]
                        ? "enabled"
                        : ""
                    }`}
                    key={key}
                  >
                    <input
                      type="checkbox"
                      checked={Boolean(
                        sections[key]
                      )}
                      onChange={() =>
                        toggleSection(
                          key
                        )
                      }
                    />

                    <span className="toggle-box">
                      {sections[key]
                        ? "✓"
                        : ""}
                    </span>

                    <span className="toggle-label">
                      {label}
                    </span>
                  </label>
                )
              )}
            </div>
          </div>

          <div className="panel-section builder-editors">
            {renderEditorSection(
              "summary",
              "Professional Summary",
              <div className="editor-stack">
                <textarea
                  className="builder-large-textarea"
                  value={
                    cvInfo.summary
                  }
                  onChange={(event) =>
                    handleInfoChange(
                      "summary",
                      event.target.value
                    )
                  }
                  placeholder="Your professional summary..."
                />

                <button
                  type="button"
                  className="inline-ai-button"
                  onClick={
                    handleAISummary
                  }
                  disabled={
                    aiBusy ===
                    "summary"
                  }
                >
                  {aiBusy ===
                  "summary"
                    ? "Generating..."
                    : "AI Improve"}
                </button>
              </div>
            )}

            {renderEditorSection(
              "skills",
              "Skills",
              <div className="editor-stack">
                <div className="editor-list">
                  {skillList.map(
                    (
                      skill,
                      index
                    ) => (
                      <div
                        className="editor-list-row"
                        key={`${skill}-${index}`}
                      >
                        <input
                          type="text"
                          value={
                            skill
                          }
                          onChange={(
                            event
                          ) =>
                            updateSkill(
                              index,
                              event.target.value
                            )
                          }
                        />

                        <button
                          type="button"
                          onClick={() =>
                            removeSkill(
                              index
                            )
                          }
                        >
                          ×
                        </button>
                      </div>
                    )
                  )}
                </div>

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addSkill
                  }
                >
                  + Add Skill
                </button>
              </div>
            )}

            {renderEditorSection(
              "experience",
              "Experience",
              <div className="editor-stack">
                {experience.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="entry-editor-card"
                      key={index}
                    >
                      <div className="entry-editor-grid">
                        <input
                          type="text"
                          value={
                            item.job_title
                          }
                          onChange={(
                            event
                          ) =>
                            updateExperience(
                              index,
                              "job_title",
                              event.target.value
                            )
                          }
                          placeholder="Job title"
                        />

                        <input
                          type="text"
                          value={
                            item.company
                          }
                          onChange={(
                            event
                          ) =>
                            updateExperience(
                              index,
                              "company",
                              event.target.value
                            )
                          }
                          placeholder="Company"
                        />

                        <input
                          type="text"
                          value={
                            item.duration
                          }
                          onChange={(
                            event
                          ) =>
                            updateExperience(
                              index,
                              "duration",
                              event.target.value
                            )
                          }
                          placeholder="2025 - Present"
                        />
                      </div>

                      <textarea
                        value={
                          item.description
                        }
                        onChange={(
                          event
                        ) =>
                          updateExperience(
                            index,
                            "description",
                            event.target.value
                          )
                        }
                        placeholder="Responsibilities and achievements..."
                      />

                      <button
                        type="button"
                        className="remove-item-button"
                        onClick={() =>
                          removeExperience(
                            index
                          )
                        }
                      >
                        Remove
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addExperience
                  }
                >
                  + Add Experience
                </button>
              </div>
            )}

            {renderEditorSection(
              "education",
              "Education",
              <div className="editor-stack">
                {education.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="entry-editor-card"
                      key={index}
                    >
                      <div className="entry-editor-grid">
                        <input
                          type="text"
                          value={
                            item.degree
                          }
                          onChange={(
                            event
                          ) =>
                            updateEducation(
                              index,
                              "degree",
                              event.target.value
                            )
                          }
                          placeholder="Degree"
                        />

                        <input
                          type="text"
                          value={
                            item.institution
                          }
                          onChange={(
                            event
                          ) =>
                            updateEducation(
                              index,
                              "institution",
                              event.target.value
                            )
                          }
                          placeholder="University / Institution"
                        />

                        <input
                          type="text"
                          value={
                            item.year
                          }
                          onChange={(
                            event
                          ) =>
                            updateEducation(
                              index,
                              "year",
                              event.target.value
                            )
                          }
                          placeholder="2022 - 2026"
                        />
                      </div>

                      <textarea
                        value={
                          item.description
                        }
                        onChange={(
                          event
                        ) =>
                          updateEducation(
                            index,
                            "description",
                            event.target.value
                          )
                        }
                        placeholder="Relevant details..."
                      />

                      <button
                        type="button"
                        className="remove-item-button"
                        onClick={() =>
                          removeEducation(
                            index
                          )
                        }
                      >
                        Remove
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addEducation
                  }
                >
                  + Add Education
                </button>
              </div>
            )}

            {renderEditorSection(
              "certifications",
              "Certifications",
              <div className="editor-stack">
                {certifications.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="entry-editor-card"
                      key={index}
                    >
                      <div className="entry-editor-grid">
                        <input
                          type="text"
                          value={
                            item.name
                          }
                          onChange={(
                            event
                          ) =>
                            updateCertification(
                              index,
                              "name",
                              event.target.value
                            )
                          }
                          placeholder="Certification / Course"
                        />

                        <input
                          type="text"
                          value={
                            item.issuer
                          }
                          onChange={(
                            event
                          ) =>
                            updateCertification(
                              index,
                              "issuer",
                              event.target.value
                            )
                          }
                          placeholder="Issuer"
                        />

                        <input
                          type="text"
                          value={
                            item.year
                          }
                          onChange={(
                            event
                          ) =>
                            updateCertification(
                              index,
                              "year",
                              event.target.value
                            )
                          }
                          placeholder="2026"
                        />
                      </div>

                      <button
                        type="button"
                        className="remove-item-button"
                        onClick={() =>
                          removeCertification(
                            index
                          )
                        }
                      >
                        Remove
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addCertification
                  }
                >
                  + Add Certification
                </button>
              </div>
            )}

            {renderEditorSection(
              "projects",
              "Projects",
              <div className="editor-stack">
                {cvProjects.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="entry-editor-card"
                      key={index}
                    >
                      <div className="entry-editor-grid">
                        <input
                          type="text"
                          value={
                            item.title
                          }
                          onChange={(
                            event
                          ) =>
                            updateProject(
                              index,
                              "title",
                              event.target.value
                            )
                          }
                          placeholder="Project title"
                        />

                        <input
                          type="text"
                          value={
                            item.target_role
                          }
                          onChange={(
                            event
                          ) =>
                            updateProject(
                              index,
                              "target_role",
                              event.target.value
                            )
                          }
                          placeholder="Role / Domain"
                        />
                      </div>

                      <textarea
                        value={
                          item.description
                        }
                        onChange={(
                          event
                        ) =>
                          updateProject(
                            index,
                            "description",
                            event.target.value
                          )
                        }
                        placeholder="Project description..."
                      />

                      <input
                        type="text"
                        value={
                          item.skills.join(
                            ", "
                          )
                        }
                        onChange={(
                          event
                        ) =>
                          updateProjectArrayField(
                            index,
                            "skills",
                            event.target.value
                          )
                        }
                        placeholder="Python, SQL, Power BI..."
                      />

                      <input
                        type="text"
                        value={
                          item.objectives.join(
                            ", "
                          )
                        }
                        onChange={(
                          event
                        ) =>
                          updateProjectArrayField(
                            index,
                            "objectives",
                            event.target.value
                          )
                        }
                        placeholder="Outcome 1, Outcome 2..."
                      />

                      <div className="entry-editor-grid">
                        <input
                          type="text"
                          value={
                            item.github_url
                          }
                          onChange={(
                            event
                          ) =>
                            updateProject(
                              index,
                              "github_url",
                              event.target.value
                            )
                          }
                          placeholder="GitHub URL"
                        />

                        <input
                          type="text"
                          value={
                            item.demo_url
                          }
                          onChange={(
                            event
                          ) =>
                            updateProject(
                              index,
                              "demo_url",
                              event.target.value
                            )
                          }
                          placeholder="Live Demo URL"
                        />
                      </div>

                      <button
                        type="button"
                        className="remove-item-button"
                        onClick={() =>
                          removeProject(
                            index
                          )
                        }
                      >
                        Remove
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addProject
                  }
                >
                  + Add Project
                </button>
              </div>
            )}

            {renderEditorSection(
              "achievements",
              "Achievements",
              <div className="editor-stack">
                {achievements.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="editor-list-row"
                      key={index}
                    >
                      <input
                        type="text"
                        value={
                          item
                        }
                        onChange={(
                          event
                        ) =>
                          updateAchievement(
                            index,
                            event.target.value
                          )
                        }
                        placeholder="Achievement / award / result"
                      />

                      <button
                        type="button"
                        onClick={() =>
                          removeAchievement(
                            index
                          )
                        }
                      >
                        ×
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addAchievement
                  }
                >
                  + Add Achievement
                </button>
              </div>
            )}

            {renderEditorSection(
              "languages",
              "Languages",
              <div className="editor-stack">
                {languages.map(
                  (
                    item,
                    index
                  ) => (
                    <div
                      className="editor-list-row"
                      key={index}
                    >
                      <input
                        type="text"
                        value={
                          item
                        }
                        onChange={(
                          event
                        ) =>
                          updateLanguage(
                            index,
                            event.target.value
                          )
                        }
                        placeholder="English — Professional"
                      />

                      <button
                        type="button"
                        onClick={() =>
                          removeLanguage(
                            index
                          )
                        }
                      >
                        ×
                      </button>
                    </div>
                  )
                )}

                <button
                  type="button"
                  className="add-item-button"
                  onClick={
                    addLanguage
                  }
                >
                  + Add Language
                </button>
              </div>
            )}

            {renderEditorSection(
              "links",
              "Professional Links",
              <div className="builder-fields">
                <label>
                  LinkedIn

                  <input
                    type="text"
                    value={
                      cvInfo.linkedin
                    }
                    onChange={(event) =>
                      handleInfoChange(
                        "linkedin",
                        event.target.value
                      )
                    }
                  />
                </label>

                <label>
                  GitHub

                  <input
                    type="text"
                    value={
                      cvInfo.github
                    }
                    onChange={(event) =>
                      handleInfoChange(
                        "github",
                        event.target.value
                      )
                    }
                  />
                </label>

                <label>
                  Portfolio

                  <input
                    type="text"
                    value={
                      cvInfo.portfolio
                    }
                    onChange={(event) =>
                      handleInfoChange(
                        "portfolio",
                        event.target.value
                      )
                    }
                  />
                </label>
              </div>
            )}
          </div>

          <div className="builder-data-quality">
            <div className="data-quality-heading">
              <span>
                DATA QUALITY
              </span>

              <strong>
                {
                  dataStatus.filter(
                    (item) =>
                      item.complete
                  ).length
                }
                /
                {dataStatus.length}
              </strong>
            </div>

            <div className="data-quality-list">
              {dataStatus.map(
                (item) => (
                  <div
                    key={
                      item.label
                    }
                    className={
                      item.complete
                        ? "data-complete"
                        : "data-missing"
                    }
                  >
                    <span>
                      {item.complete
                        ? "✓"
                        : "○"}
                    </span>

                    {item.label}
                  </div>
                )
              )}
            </div>
          </div>
        </aside>

        <section className="cv-preview-wrapper">
          <div className="preview-toolbar">
            <div>
              <span className="preview-label">
                LIVE CV PREVIEW
              </span>

              <span className="preview-description">
                A4 professional layout •
                template:
                {` `}
                {template}
              </span>
            </div>

            <div className="preview-toolbar-actions">
              <span className="a4-badge">
                A4
              </span>

              <button
                type="button"
                className="preview-print-button"
                onClick={
                  handlePrint
                }
              >
                Print
              </button>
            </div>
          </div>

          <div
            className={`cv-paper cv-template-${template}`}
            id="cv-document"
          >
            <header className="cv-header">
              <div className="cv-header-identity">
                <h1>
                  {cvInfo.name ||
                    "Your Name"}
                </h1>

                <h2>
                  {cvInfo.title ||
                    "Professional Title"}
                </h2>
              </div>

              <div className="contact-info">
                {cvInfo.email && (
                  <span>
                    {cvInfo.email}
                  </span>
                )}

                {cvInfo.phone && (
                  <span>
                    {cvInfo.phone}
                  </span>
                )}

                {cvInfo.location && (
                  <span>
                    {cvInfo.location}
                  </span>
                )}

                {cvInfo.linkedin && (
                  <span>
                    {cvInfo.linkedin}
                  </span>
                )}

                {cvInfo.github && (
                  <span>
                    {cvInfo.github}
                  </span>
                )}

                {cvInfo.portfolio && (
                  <span>
                    {cvInfo.portfolio}
                  </span>
                )}
              </div>
            </header>

            {sections.summary &&
              cvInfo.summary && (
                <section className="cv-section">
                  <h3>
                    Professional Summary
                  </h3>

                  <p>
                    {cvInfo.summary}
                  </p>
                </section>
              )}

            {sections.skills &&
              skillList.length > 0 && (
                <section className="cv-section">
                  <h3>
                    Technical Skills
                  </h3>

                  <div className="cv-skills">
                    {skillList.map(
                      (
                        skill,
                        index
                      ) => (
                        <span
                          key={`${skill}-${index}`}
                        >
                          {skill}
                        </span>
                      )
                    )}
                  </div>
                </section>
              )}

            {sections.experience &&
              experience.length > 0 && (
                <section className="cv-section">
                  <h3>
                    Experience
                  </h3>

                  {experience.map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        className="cv-entry"
                        key={index}
                      >
                        <div className="entry-header">
                          <strong>
                            {item.job_title ||
                              "Professional Experience"}
                          </strong>

                          {item.duration && (
                            <span>
                              {item.duration}
                            </span>
                          )}
                        </div>

                        {item.company && (
                          <div className="entry-company">
                            {item.company}
                          </div>
                        )}

                        {item.description && (
                          <p>
                            {item.description}
                          </p>
                        )}
                      </div>
                    )
                  )}
                </section>
              )}

            {sections.education &&
              education.length > 0 && (
                <section className="cv-section">
                  <h3>
                    Education
                  </h3>

                  {education.map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        className="cv-entry"
                        key={index}
                      >
                        <div className="entry-header">
                          <strong>
                            {item.degree ||
                              "Education"}
                          </strong>

                          {item.year && (
                            <span>
                              {item.year}
                            </span>
                          )}
                        </div>

                        {item.institution && (
                          <div className="entry-company">
                            {item.institution}
                          </div>
                        )}

                        {item.description && (
                          <p>
                            {item.description}
                          </p>
                        )}
                      </div>
                    )
                  )}
                </section>
              )}

            {sections.certifications &&
              certifications.length > 0 && (
                <section className="cv-section">
                  <h3>
                    Certifications & Training
                  </h3>

                  {certifications.map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        className="cv-entry compact-entry"
                        key={index}
                      >
                        <div className="entry-header">
                          <strong>
                            {item.name}
                          </strong>

                          {item.year && (
                            <span>
                              {item.year}
                            </span>
                          )}
                        </div>

                        {item.issuer && (
                          <div className="entry-company">
                            {item.issuer}
                          </div>
                        )}
                      </div>
                    )
                  )}
                </section>
              )}

            {sections.projects &&
              cvProjects.length > 0 && (
                <section className="cv-section">
                  <h3>
                    Selected Projects
                  </h3>

                  {cvProjects.map(
                    (
                      project,
                      index
                    ) => (
                      <div
                        className="cv-entry"
                        key={index}
                      >
                        <div className="entry-header">
                          <strong>
                            {project.title ||
                              "Project"}
                          </strong>
                        </div>

                        {project.target_role && (
                          <div className="entry-company">
                            {project.target_role}
                          </div>
                        )}

                        {project.description && (
                          <p>
                            {project.description}
                          </p>
                        )}

                        {project.objectives
                            .length >
                            0 && (
                          <ul className="project-objectives">
                            {project.objectives
                              .slice(
                                0,
                                4
                              )
                              .map(
                                (
                                  objective,
                                  objectiveIndex
                                ) => (
                                  <li
                                    key={
                                      objectiveIndex
                                    }
                                  >
                                    {objective}
                                  </li>
                                )
                              )}
                          </ul>
                        )}

                        {project.skills
                            .length >
                            0 && (
                          <div className="project-skills">
                            {project.skills.map(
                              (
                                skill,
                                skillIndex
                              ) => (
                                <span
                                  key={
                                    skillIndex
                                  }
                                >
                                  {skill}
                                </span>
                              )
                            )}
                          </div>
                        )}

                        {(project.github_url ||
                          project.demo_url) && (
                          <div className="project-links">
                            {project.github_url && (
                              <span>
                                GitHub:
                                {` `}
                                {project.github_url}
                              </span>
                            )}

                            {project.demo_url && (
                              <span>
                                Demo:
                                {` `}
                                {project.demo_url}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  )}
                </section>
              )}

            {sections.achievements &&
              achievements.filter(
                Boolean
              ).length > 0 && (
                <section className="cv-section">
                  <h3>
                    Achievements
                  </h3>

                  <ul className="cv-bullet-list">
                    {achievements
                      .filter(
                        Boolean
                      )
                      .map(
                        (
                          item,
                          index
                        ) => (
                          <li
                            key={
                              index
                            }
                          >
                            {item}
                          </li>
                        )
                      )}
                  </ul>
                </section>
              )}

            {sections.languages &&
              languages.filter(
                Boolean
              ).length > 0 && (
                <section className="cv-section">
                  <h3>
                    Languages
                  </h3>

                  <div className="cv-inline-list">
                    {languages
                      .filter(
                        Boolean
                      )
                      .map(
                        (
                          item,
                          index
                        ) => (
                          <span
                            key={
                              index
                            }
                          >
                            {item}
                          </span>
                        )
                      )}
                  </div>
                </section>
              )}

            {sections.links &&
              (
                cvInfo.linkedin ||
                cvInfo.github ||
                cvInfo.portfolio
              ) && (
                <section className="cv-section">
                  <h3>
                    Professional Links
                  </h3>

                  <div className="links-grid">
                    {cvInfo.linkedin && (
                      <div>
                        <strong>
                          LinkedIn
                        </strong>

                        <span>
                          {cvInfo.linkedin}
                        </span>
                      </div>
                    )}

                    {cvInfo.github && (
                      <div>
                        <strong>
                          GitHub
                        </strong>

                        <span>
                          {cvInfo.github}
                        </span>
                      </div>
                    )}

                    {cvInfo.portfolio && (
                      <div>
                        <strong>
                          Portfolio
                        </strong>

                        <span>
                          {cvInfo.portfolio}
                        </span>
                      </div>
                    )}
                  </div>
                </section>
              )}

            {!cvInfo.name &&
              !cvInfo.title &&
              !cvInfo.summary &&
              skillList.length === 0 &&
              experience.length === 0 &&
              education.length === 0 &&
              certifications.length ===
                0 &&
              cvProjects.length === 0 && (
                <div className="cv-preview-empty">
                  <strong>
                    Your professional CV
                    preview is ready.
                  </strong>

                  <span>
                    Start filling the editor
                    on the left to build your
                    final CV.
                  </span>
                </div>
              )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default CVBuilder;