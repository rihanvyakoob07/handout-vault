import React from "react";
import { useTheme } from "../contexts/ThemeContext";

export default function TopBar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="h-16 bg-white dark:bg-gray-900 border-b flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Handout Vault
      </h1>

      <button
        onClick={toggleTheme}
        className="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 text-sm"
      >
        {theme === "light" ? "Dark Mode" : "Light Mode"}
      </button>
    </div>
  );
}
