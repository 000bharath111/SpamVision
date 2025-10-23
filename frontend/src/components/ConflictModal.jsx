// src/components/ConflictModal.jsx
import React from "react";

/**
 * Small confirmation modal to show when user's label conflicts with model
 * (e.g. user marking ham while model predicted spam).
 * Use from Review UI when needed.
 */
export default function ConflictModal({ open, onClose, onConfirm, title = "Conflict detected", conflictText = "", suggested = "" }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg p-6 w-96">
        <h3 className="font-semibold text-lg mb-2">{title}</h3>
        <div className="text-sm text-slate-600 mb-4">{conflictText}</div>
        <div className="mb-4 text-xs">
          <div><strong>Model suggested:</strong> {suggested}</div>
        </div>
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-3 py-2 border rounded">Cancel</button>
          <button onClick={onConfirm} className="px-3 py-2 bg-red-600 text-white rounded">Override</button>
        </div>
      </div>
    </div>
  );
}
