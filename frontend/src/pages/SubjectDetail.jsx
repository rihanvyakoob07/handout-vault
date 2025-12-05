import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function SubjectDetail() {
  const { id } = useParams();

  const [versions, setVersions] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    (async () => {
      const res = await api.get(`/handouts/${id}/versions`, {
        headers: { Authorization: "HANDOUTVAULTSECRET123" }
      });

      setVersions(res.data);
      if (res.data.length) setSelected(res.data[0]);
    })();
  }, [id]);

  const download = async (ver) => {
    const res = await api.get(`/handouts/${id}/versions/${ver.id}/download`, {
      headers: { Authorization: "HANDOUTVAULTSECRET123" },
      responseType: "blob"
    });

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = ver.file_path.split("/").pop();
    a.click();
  };

  return (
    <div className="ml-64 flex h-screen bg-gray-50">

      {/* LEFT PANEL */}
      <aside className="w-64 bg-white border-r p-5 overflow-y-auto shadow-sm">
        <h3 className="font-semibold mb-4 text-gray-800 text-lg">
          Versions
        </h3>

        <ul className="space-y-2">
          {versions.map((v) => (
            <li
              key={v.id}
              onClick={() => setSelected(v)}
              className={`p-3 rounded-lg cursor-pointer transition ${
                selected?.id === v.id
                  ? "bg-blue-600 text-white shadow"
                  : "hover:bg-gray-100"
              }`}
            >
              Version {v.version}
            </li>
          ))}
        </ul>
      </aside>

      {/* CENTER PREVIEW */}
      <main className="flex-1 p-8 overflow-y-auto">
        {selected ? (
          <>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              {id} — v{selected.version}
            </h2>

            <div className="bg-white border rounded-xl shadow p-4">
              <iframe
                src={`/handouts/preview/${selected.id}`}
                className="w-full h-[600px] rounded-md border"
              />
            </div>

            <button
              onClick={() => download(selected)}
              className="
                mt-6 bg-blue-600 text-white 
                px-5 py-2 rounded-lg 
                hover:bg-blue-700 
                transition shadow-sm
              "
            >
              Download File
            </button>
          </>
        ) : (
          <p>No versions available.</p>
        )}
      </main>

      {/* RIGHT INFO PANEL */}
      <aside className="w-80 bg-white border-l p-6 shadow-sm overflow-y-auto">
        {selected && (
          <>
            <h3 className="font-semibold mb-4 text-gray-900 text-lg">
              File Details
            </h3>

            <div className="space-y-2 text-gray-700">
              <p><b>Type:</b> {selected.file_type}</p>
              <p><b>Size:</b> {(selected.file_size / 1024).toFixed(1)} KB</p>
              <p><b>Checksum:</b> {selected.checksum}</p>
              <p><b>Uploaded:</b> {new Date(selected.created_at).toLocaleString()}</p>
              <p><b>Downloads:</b> {selected.downloads}</p>
              <p><b>Previews:</b> {selected.previews}</p>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
