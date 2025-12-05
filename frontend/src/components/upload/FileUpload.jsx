import React, { useState, useRef } from "react";
import api from "./../../services/api";

export default function UploadModal({ isOpen, onClose, subjects, refresh }) {
  const [subject, setSubject] = useState("");
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);

  const [previewName, setPreviewName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const dropRef = useRef();

  if (!isOpen) return null;

  // ---------------- DRAG & DROP HANDLERS ----------------
  const handleDragOver = (e) => {
    e.preventDefault();
    dropRef.current.classList.add("border-blue-500");
  };

  const handleDragLeave = () => {
    dropRef.current.classList.remove("border-blue-500");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    dropRef.current.classList.remove("border-blue-500");
    const f = e.dataTransfer.files[0];
    setFile(f);
    setPreviewName(f.name);
  };

  const handleFileSelect = (e) => {
    const f = e.target.files[0];
    setFile(f);
    setPreviewName(f.name);
  };

  // ------------------ UPLOAD ------------------
  const upload = async () => {
    if (!subject || !title || !file) {
      alert("Fill all fields");
      return;
    }

    setUploading(true);

    const form = new FormData();
    form.append("subject", subject);
    form.append("title", title);
    form.append("file", file);

    try {
      await api.post("/handouts/upload", form, {
        headers: { Authorization: "HANDOUTVAULTSECRET123" },
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded * 100) / e.total));
        },
      });

      setUploading(false);
      refresh(); // reload handouts UI
      onClose();
    } catch (err) {
      console.error(err);
      alert("Upload failed");
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white w-[450px] rounded-xl shadow-xl p-6 animate-fadeIn">

        <h2 className="text-xl font-semibold mb-4">Upload Handout</h2>

        {/* SUBJECT DROPDOWN */}
        <label className="block mb-2">Subject</label>
        <select
          className="w-full border p-2 rounded mb-4"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        >
          <option value="">Select subject</option>
          {subjects.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
          <option value="__new">+ Add New Subject</option>
        </select>

        {/* NEW SUBJECT INPUT */}
        {subject === "__new" && (
          <input
            className="w-full border p-2 rounded mb-4"
            placeholder="Enter new subject name"
            onChange={(e) => setSubject(e.target.value)}
          />
        )}

        {/* TITLE */}
        <label className="block mb-2">Handout Title</label>
        <input
          className="w-full border p-2 rounded mb-4"
          placeholder="Enter title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        {/* DRAG & DROP ZONE */}
        <div
          ref={dropRef}
          className="border-2 border-dashed border-gray-400 rounded-lg p-6 text-center cursor-pointer transition"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!file ? (
            <>
              <p className="text-gray-600">Drag & Drop file here</p>
              <p className="text-sm text-gray-500">or click to select</p>
              <input type="file" className="hidden" onChange={handleFileSelect} id="filePicker" />
              <button
                className="mt-3 px-4 py-1 bg-gray-200 rounded"
                onClick={() => document.getElementById("filePicker").click()}
              >Browse</button>
            </>
          ) : (
            <p className="text-blue-600 font-medium">{previewName}</p>
          )}
        </div>

        {/* PROGRESS BAR */}
        {uploading && (
          <div className="w-full bg-gray-200 rounded-full h-3 mt-4">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* ACTION BUTTONS */}
        <div className="flex justify-end mt-6 space-x-3">
          <button className="px-4 py-2 bg-gray-300 rounded" onClick={onClose}>
            Cancel
          </button>

          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={upload}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>
    </div>
  );
}
