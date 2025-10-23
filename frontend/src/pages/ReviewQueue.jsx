// src/pages/ReviewQueue.jsx
import React, { useEffect, useState } from "react";
import { getReviewQueue, submitReview } from "../api/client";

export default function ReviewQueue() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadQueue(); }, []);

  async function loadQueue() {
    setLoading(true);
    try {
      const resp = await getReviewQueue(50);
      setItems(resp.items || resp || []);
    } catch (e) {
      console.error(e);
      alert("Failed to load review queue");
    } finally { setLoading(false); }
  }

  async function doAction(item, label) {
    try {
      await submitReview({ id: item.id, label });
      setItems(items.filter(i => i.id !== item.id));
    } catch (e) {
      alert("Failed to submit review: " + e.message);
    }
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">Review Queue</h2>
      {loading ? <div>Loading…</div> : null}
      <div className="space-y-3">
        {items.length === 0 ? <div className="text-sm text-slate-500">No pending items.</div> : null}
        {items.map(it => (
          <div key={it.id} className="p-3 border rounded flex flex-col md:flex-row md:items-center gap-3">
            <div className="flex-1">
              <div className="text-sm text-slate-600">Score: {it.score !== null ? (it.score*100).toFixed(2) + "%" : "—"}</div>
              <div className="mt-2 font-mono break-words">{it.text}</div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => doAction(it, "spam")} className="px-3 py-2 bg-red-600 text-white rounded">Mark Spam</button>
              <button onClick={() => doAction(it, "ham")} className="px-3 py-2 bg-green-600 text-white rounded">Mark Ham</button>
              <button onClick={() => doAction(it, "skip")} className="px-3 py-2 border rounded">Skip</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
