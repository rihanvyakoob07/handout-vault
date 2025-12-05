import React from "react";
import { Book, UploadCloud, Users, FileClock } from "lucide-react";

const tiles = [
  {
    title: "Total Subjects",
    value: "04",
    icon: Book,
  },
  {
    title: "Total Handouts",
    value: "128",
    icon: UploadCloud,
  },
  {
    title: "Active Users",
    value: "312",
    icon: Users,
  },
  {
    title: "Recent Uploads",
    value: "12",
    icon: FileClock,
  },
];

export default function Dashboard() {
  return (
    <div className="p-8 space-y-10">
      <h1 className="text-2xl font-bold dark:text-white">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {tiles.map((t) => {
          const Icon = t.icon;
          return (
            <div
              key={t.title}
              className="
                bg-white dark:bg-gray-800 
                p-6 rounded-xl shadow hover:shadow-lg 
                transition cursor-pointer
                border border-gray-200 dark:border-gray-700
              "
            >
              <Icon className="w-8 h-8 text-blue-500 mb-4" />
              <div className="text-gray-500 dark:text-gray-400 text-sm">{t.title}</div>
              <div className="text-3xl font-bold dark:text-white">{t.value}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
