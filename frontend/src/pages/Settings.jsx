// src/pages/Settings.jsx
import React, { useState } from "react";

export default function Settings() {
  const [apiBase, setApiBase] = useState(import.meta.env.VITE_API_BASE || (process.env.REACT_APP_API_BASE || "http://localhost:8000"));

  function save() {
    // For demonstration: in production you'd persist to server or to localStorage
    localStorage.setItem("api_base", apiBase);
    alert("Saved (local)");
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">Settings</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-slate-600">API Base URL</label>
          <input value={apiBase} onChange={(e)=>setApiBase(e.target.value)} className="mt-1 p-2 border rounded w-full" />
        </div>
        <div>
          <label className="text-sm text-slate-600">UI Theme</label>
          <select className="mt-1 p-2 border rounded w-full">
            <option>Light (default)</option>
            <option>Dark</option>
          </select>
        </div>
      </div>

      <div className="mt-4">
        <button onClick={save} className="px-4 py-2 bg-indigo-600 text-white rounded">Save</button>
      </div>
    </div>
  );
}
