import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";

import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import Profile from "./pages/Profile";
import MyCV from "./pages/MyCV";
import JobMatcher from "./pages/JobMatcher";
import Chat from "./pages/Chat";
import Interview from "./pages/Interview";
import Projects from "./pages/Projects";
import Portfolio from "./pages/Portfolio";
import CVBuilder from "./pages/CVBuilder";
import SocialCallback from "./pages/SocialCallback";
import Layout from "./components/Layout";
import TailoredCV from "./pages/TailoredCV";

import EmailVerified from "./pages/EmailVerified";
import ResetPassword from "./pages/ResetPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* =========================
            Public Pages
        ========================= */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/reset-password/:uid/:token"
          element={<ResetPassword />}
        />

        <Route
          path="/social-callback"
          element={<SocialCallback />}
        />

        <Route
          path="/email-verified"
          element={<EmailVerified />}
        />

        {/* =========================
            Protected Pages
        ========================= */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/cv"
          element={
            <ProtectedRoute>
              <Layout>
                <MyCV />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/cv-builder"
          element={
            <ProtectedRoute>
              <Layout>
                <CVBuilder />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/jobs"
          element={
            <ProtectedRoute>
              <Layout>
                <JobMatcher />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Layout>
                <Chat />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/interview"
          element={
            <ProtectedRoute>
              <Layout>
                <Interview />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Layout>
                <Projects />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <Layout>
                <Portfolio />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/tailored-cv"
          element={
            <ProtectedRoute>
              <Layout>
                <TailoredCV />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* =========================
            Home Page
        ========================= */}

        <Route
          path="/"
          element={<Login />}
        />

        {/* =========================
            Fallback
        ========================= */}

        <Route
          path="*"
          element={<Login />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;