// src/components/ResultCard.jsx
import React from "react";

export default function ResultCard({ result, className = "" }) {
  if (!result) return null;
  const p = result.spam_probability ?? null;
  const label = result.label;
  const colorClass = label === "spam" ? "bg-red-50 border-red-200" : "bg-green-50 border-green-200";
  return (
    <div className={`border rounded-lg p-4 ${colorClass} ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-500">Prediction</div>
          <div className="text-xl font-semibold">{label?.toUpperCase() ?? "—"}</div>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-500">Spam probability</div>
          <div className="text-lg font-medium">{p !== null ? (p * 100).toFixed(2) + "%" : "N/A"}</div>
        </div>
      </div>

      {result.model_version ? <div className="mt-3 text-xs text-slate-500">Model: {result.model_version}</div> : null}
    </div>
  );
}
