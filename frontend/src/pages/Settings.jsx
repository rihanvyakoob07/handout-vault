import React from "react";
import { useAuth } from "../contexts/AuthContext";

export default function Settings() {
  const { user, role, logout } = useAuth();
  return (
    <div className="ml-64 p-6">
      <h2 className="text-2xl font-semibold mb-4">Settings</h2>
      <div className="bg-white p-6 rounded shadow w-80">
        <p>Email: {user?.email}</p>
        <p>Role: {role}</p>

        <button
          onClick={logout}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
