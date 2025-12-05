// src/pages/HandoutsInSubject.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";

export default function HandoutsInSubject() {
  const { subject } = useParams();
  const [handouts, setHandouts] = useState([]);

  useEffect(() => {
    (async () => {
      const res = await api.get(`/handouts/subject/${subject}`, {
        headers: { Authorization: "HANDOUTVAULTSECRET123" }
      });
      setHandouts(res.data);
    })();
  }, [subject]);

  return (
    <div className="ml-64 px-10 py-10">
      <h1 className="text-3xl font-bold mb-8">{subject}</h1>

      {handouts.length === 0 ? (
        <p>No handouts yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {handouts.map(h => (
            <Link
              key={h.id}
              to={`/handout/${h.id}`}
              className="p-6 bg-white rounded-xl shadow hover:shadow-lg transition"
            >
              <h3 className="text-xl font-semibold mb-2">{h.title}</h3>
              <p className="text-gray-500 text-sm">
                Latest version: {h.latest_version}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
