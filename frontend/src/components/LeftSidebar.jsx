import React from "react";
import { NavLink } from "react-router-dom";
import { Home, Book, Clock, Trash, Settings } from "lucide-react";

const menu = [
  { name: "Home", icon: Home, path: "/" },
  { name: "Subjects", icon: Book, path: "/subjects" },
  { name: "Recents", icon: Clock, path: "/recents" },
  { name: "Trash", icon: Trash, path: "/trash" },
  { name: "Settings", icon: Settings, path: "/settings" },
];

export default function LeftSidebar() {
  return (
    <div
      className="
        fixed left-0 top-0 h-full w-64
        bg-white dark:bg-gray-900
        border-r border-gray-200 dark:border-gray-700
        shadow-sm z-40
      "
    >
      <div className="px-6 py-5 text-xl font-bold dark:text-white">
        Handout Vault
      </div>

      <nav className="mt-4 flex flex-col gap-1">
        {menu.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `
                flex items-center gap-3 px-6 py-3
                font-medium text-sm
                transition-all
                ${isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                }
              `
              }
            >
              <Icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
