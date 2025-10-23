// src/components/SHAPViz.jsx
import React from "react";

/**
 * Simple SHAP-like bar chart visualization.
 * Expects payload: { feature_importances: [{name, value}, ...] } or fallback tokens.
 */
export default function SHAPViz({ payload }) {
  if (!payload) return null;
  const items = payload.feature_importances || payload.features || [];

  // normalize absolute values for bar widths
  const max = Math.max(...items.map(i => Math.abs(i.value) || 0), 1);
  return (
    <div className="mt-2">
      {items.length === 0 ? <div className="text-sm text-slate-500">No explanation available.</div> : null}
      <div className="space-y-2">
        {items.slice(0, 12).map((it, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className="w-28 text-xs text-slate-600">{it.name}</div>
            <div className="flex-1 bg-slate-100 rounded overflow-hidden h-4">
              <div
                style={{ width: `${(Math.abs(it.value) / max) * 100}%` }}
                className={`h-4 ${it.value > 0 ? "bg-red-400" : "bg-green-400"}`}
              />
            </div>
            <div className="w-14 text-right text-xs font-mono">{it.value.toFixed(3)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
