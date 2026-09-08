import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import "./Layout.css";

function Layout({ children }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navItems = [
    {
      to: "/dashboard",
      label: "Dashboard",
      icon: "⌂",
    },
    {
      to: "/cv",
      label: "My CV",
      icon: "▤",
    },
    {
      to: "/cv-builder",
      label: "CV Builder",
      icon: "✦",
    },
    {
      to: "/tailored-cv",
      label: "Tailored CV",
      icon: "◎",
    },
    {
      to: "/jobs",
      label: "Job Matcher",
      icon: "◈",
    },
    {
      to: "/projects",
      label: "My Projects",
      icon: "◆",
    },
    {
      to: "/portfolio",
      label: "Portfolio",
      icon: "◇",
    },
    {
      to: "/chat",
      label: "AI Career Chat",
      icon: "◌",
    },
    {
      to: "/interview",
      label: "Interview Simulator",
      icon: "◉",
    },
    {
      to: "/profile",
      label: "Profile",
      icon: "○",
    },
  ];

  return (
    <div className="app-layout">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">

        {/* Brand */}

        <div className="brand">

          <div className="brand-icon">
            AI
          </div>

          <div className="brand-content">
            <div className="brand-name">
              Career
            </div>

            <div className="brand-subtitle">
              Assistant
            </div>
          </div>

        </div>


        {/* Navigation */}

        <nav className="sidebar-nav">

          <div className="nav-section-label">
            WORKSPACE
          </div>

          {navItems
            .slice(0, 7)
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-item ${
                    isActive
                      ? "active"
                      : ""
                  }`
                }
              >
                <span className="nav-icon">
                  {item.icon}
                </span>

                <span className="nav-label">
                  {item.label}
                </span>
              </NavLink>
            ))}


          <div className="nav-section-label nav-section-secondary">
            AI TOOLS
          </div>

          {navItems
            .slice(7)
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-item ${
                    isActive
                      ? "active"
                      : ""
                  }`
                }
              >
                <span className="nav-icon">
                  {item.icon}
                </span>

                <span className="nav-label">
                  {item.label}
                </span>
              </NavLink>
            ))}

        </nav>


        {/* Sidebar Footer */}

        <div className="sidebar-footer">

          <div className="sidebar-footer-divider" />

          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
            <span className="logout-icon">
              ↪
            </span>

            <span className="logout-label">
              Logout
            </span>
          </button>

        </div>

      </aside>


      {/* =================================================
          MAIN AREA
      ================================================= */}

      <div className="main-area">

        {/* Topbar */}

        <header className="topbar">

          <div className="topbar-inner">

            <div className="topbar-title">
              AI Career Assistant
            </div>

            <div className="topbar-status">
              <span className="status-dot" />
              <span>
                Career workspace
              </span>
            </div>

          </div>

        </header>


        {/* Content */}

        <main className="page-content">

          <div className="page-content-inner">
            {children}
          </div>

        </main>

      </div>

    </div>
  );
}

export default Layout;