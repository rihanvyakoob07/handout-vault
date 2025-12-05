import React from "react";

export default function RightSidebar({ children, title = "Details" }) {
  return (
    <div
      className="
        fixed right-0 top-0 h-full w-72
        bg-white dark:bg-gray-900
        border-l border-gray-200 dark:border-gray-700
        p-5 overflow-y-auto
      "
    >
      <h2 className="text-lg font-semibold mb-4 dark:text-white">{title}</h2>
      {children}
    </div>
  );
}
