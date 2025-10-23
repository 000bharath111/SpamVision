// src/pages/ModelManager.jsx
import React, { useState, useEffect } from "react";
import { getModels, uploadModel, activateModel } from "../api/client";

export default function ModelManager() {
  const [models, setModels] = useState([]);
  const [file, setFile] = useState(null);
  const [version, setVersion] = useState("");
  const [threshold, setThreshold] = useState(0.5);

  useEffect(() => { loadModels(); }, []);

  async function loadModels() {
    try {
      const list = await getModels();
      setModels(list || []);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!file || !version) return alert("Provide version and .joblib file");
    try {
      await uploadModel(file, version, threshold);
      alert("Uploaded");
      setFile(null);
      setVersion("");
      loadModels();
    } catch (err) {
      alert("Upload failed: " + err.message);
    }
  }

  async function doActivate(ver) {
    try {
      await activateModel(ver);
      alert("Activated " + ver);
      loadModels();
    } catch (e) {
      alert("Activate failed: " + e.message);
    }
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-6">
      <h2 className="text-lg font-semibold">Model Manager</h2>

      <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
        <div>
          <label className="block text-sm text-slate-600">Version</label>
          <input value={version} onChange={(e) => setVersion(e.target.value)} placeholder="v20251021" className="mt-1 p-2 border rounded w-full" />
        </div>
        <div>
          <label className="block text-sm text-slate-600">Threshold</label>
          <input type="number" step="0.01" min="0" max="1" value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} className="mt-1 p-2 border rounded w-full" />
        </div>
        <div>
          <label className="block text-sm text-slate-600">Artifact (.joblib)</label>
          <input type="file" accept=".joblib" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="mt-1" />
        </div>
        <div className="md:col-span-3">
          <button type="submit" className="mt-3 px-4 py-2 bg-indigo-600 text-white rounded">Upload</button>
        </div>
      </form>

      <section>
        <h3 className="font-medium mb-2">Available models</h3>
        <div className="space-y-2">
          {models.map(m => (
            <div className="p-3 border rounded flex items-center justify-between" key={m.version}>
              <div>
                <div className="font-medium">{m.version}</div>
                <div className="text-xs text-slate-500">{m.created_at}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-600">thr: {m.threshold ?? "0.5"}</div>
                <button onClick={() => doActivate(m.version)} className="px-3 py-1 bg-emerald-600 text-white rounded">Activate</button>
              </div>
            </div>
          ))}
          {models.length === 0 && <div className="text-slate-500 text-sm">No models yet</div>}
        </div>
      </section>
    </div>
  );
}
