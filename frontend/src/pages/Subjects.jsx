import React, { useEffect, useState } from "react";
import api from "./../services/api";
import { Link } from "react-router-dom";
import UploadModal from "./../components/upload/FileUpload";

export default function Subjects() {
  const FIXED_SUBJECTS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Computer Science"
  ];

  const [subjects, setSubjects] = useState([]);
  const [showUpload, setShowUpload] = useState(false);

  // ---------------------------
  // Load subjects from backend
  // ---------------------------
  const loadSubjects = async () => {
    try {
      const res = await api.get("/handouts/subjects", {
        headers: { Authorization: "HANDOUTVAULTSECRET123" }
      });

      // backend returns: [{id:"Physics",count:3}, ...]
      const list = FIXED_SUBJECTS.map((name) => {
        const found = res.data.find((x) => x.id === name);
        return {
          id: name,
          count: found ? found.count : 0,
        };
      });

      setSubjects(list);
    } catch (err) {
      console.error("Failed to load subjects:", err);
    }
  };

  useEffect(() => {
    loadSubjects();
  }, []);

  return (
    <div className="ml-64 px-10 py-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Subjects</h1>

        <button
          onClick={() => setShowUpload(true)}
          className="
            px-4 py-2 bg-blue-600 text-white rounded-lg shadow 
            hover:bg-blue-700 transition
          "
        >
          + Upload Handout
        </button>
      </div>

      {/* Upload modal */}
      <UploadModal
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        subjects={FIXED_SUBJECTS}
        refresh={loadSubjects}   // <-- FIXED REFRESH
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {subjects.map((s) => (
          <Link
            key={s.id}
            to={`/subjects/${s.id}`}
            className="
              bg-white border rounded-xl shadow-sm
              hover:shadow-lg hover:-translate-y-1 
              transition-all duration-200 p-6
            "
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {s.id}
            </h3>
            <p className="text-gray-600 text-sm">
              {s.count} handouts available
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
