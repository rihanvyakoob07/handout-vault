// frontend/src/pages/Home.jsx

import React from "react";
import Dashboard from "../components/Dashboard";
import TopBar from "../components/TopBar";

export default function Home() {
  return (
    <div className="ml-64 h-full bg-gray-50">
      <TopBar />
      <div className="p-8">
        <Dashboard />
      </div>
    </div>
  );
}
