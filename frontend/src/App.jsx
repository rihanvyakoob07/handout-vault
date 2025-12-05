// src/App.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import LeftSidebar from "./components/LeftSidebar";
import TopBar from "./components/TopBar";

import Home from "./pages/Home";
import Subjects from "./pages/Subjects";
import HandoutsInSubject from "./pages/HandoutsInSubject";
import SubjectDetail from "./pages/SubjectDetail";
import Recents from "./pages/Recents";
import Trash from "./pages/Trash";
import Settings from "./pages/Settings";
import Login from "./pages/Login";

import { useAuth } from "./contexts/AuthContext";

function ProtectedLayout({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="p-6">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex">
      {/* Sidebar */}
      <LeftSidebar />

      {/* Content Area */}
      <div className="flex-1 ml-64">
        <TopBar />
        <div className="pt-4 px-6">{children}</div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      {/* LOGIN → Public */}
      <Route path="/login" element={<Login />} />

      {/* HOME */}
      <Route
        path="/"
        element={
          <ProtectedLayout>
            <Home />
          </ProtectedLayout>
        }
      />

      {/* SUBJECTS PAGE */}
      <Route
        path="/subjects"
        element={
          <ProtectedLayout>
            <Subjects />
          </ProtectedLayout>
        }
      />

      {/* HANDOUT LIST INSIDE SUBJECT */}
      <Route
        path="/subject/:subject"
        element={
          <ProtectedLayout>
            <HandoutsInSubject />
          </ProtectedLayout>
        }
      />

      {/* VERSION DETAIL */}
      <Route
        path="/handout/:id"
        element={
          <ProtectedLayout>
            <SubjectDetail />
          </ProtectedLayout>
        }
      />

      {/* RECENTS */}
      <Route
        path="/recents"
        element={
          <ProtectedLayout>
            <Recents />
          </ProtectedLayout>
        }
      />

      {/* TRASH */}
      <Route
        path="/trash"
        element={
          <ProtectedLayout>
            <Trash />
          </ProtectedLayout>
        }
      />

      {/* SETTINGS */}
      <Route
        path="/settings"
        element={
          <ProtectedLayout>
            <Settings />
          </ProtectedLayout>
        }
      />
    </Routes>
  );
}
