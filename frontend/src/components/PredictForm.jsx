// src/components/PredictForm.jsx
import React, { useState } from "react";
import { predict } from "../api/client";

export default function PredictForm({ onResult = () => {}, onExplain = () => {} }) {
  const [text, setText] = useState("");
  const [threshold, setThreshold] = useState(0.5);
  const [loading, setLoading] = useState(false);

  async function handlePredict(explain = false) {
    if (!text.trim()) return alert("Enter a message to predict.");
    setLoading(true);
    try {
      const resp = await predict(text, Number(threshold));
      // If API supported explain=true and returned explanation, handle it
      onResult(resp);
      // For this UI, we call explain separately if available (server-side).
      // If resp.explanation exists, forward it
      if (resp.explanation) onExplain(resp, resp.explanation);
    } catch (e) {
      alert("Prediction failed: " + e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea
        className="w-full p-3 border rounded-md min-h-[120px] text-sm"
        placeholder="Paste an SMS message, e.g. 'Free entry! Claim prize now...'"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="mt-3 flex items-center gap-4">
        <label className="text-sm text-slate-600 flex items-center gap-2">
          Threshold:
          <input type="range" min="0" max="1" step="0.01" value={threshold} onChange={(e) => setThreshold(e.target.value)} />
          <span className="w-12 text-right font-medium">{Number(threshold).toFixed(2)}</span>
        </label>
        <button onClick={() => handlePredict(false)} disabled={loading} className="ml-auto bg-indigo-600 text-white px-4 py-2 rounded shadow">
          {loading ? "Predicting..." : "Predict"}
        </button>
        <button onClick={() => handlePredict(true)} disabled={loading} className="bg-white border px-4 py-2 rounded">
          {loading ? "Please wait" : "Predict + Explain"}
        </button>
      </div>
    </div>
  );
}
