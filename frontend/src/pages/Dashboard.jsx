// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import { getMetrics, getModels } from "../api/client";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetchMetrics();
    fetchModels();
  }, []);

  async function fetchMetrics() {
    try {
      const m = await getMetrics();
      setMetrics(m || {});
    } catch (e) {
      console.warn("Failed to fetch metrics", e);
    }
  }

  async function fetchModels() {
    try {
      const list = await getModels();
      setModels(list || []);
    } catch (e) {
      console.warn("Failed to fetch models", e);
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 bg-white p-6 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-4">System Dashboard</h2>
        <div className="grid grid-cols-2 gap-4">
          <MetricCard title="Messages / day" value={metrics?.messages_per_day ?? "—"} />
          <MetricCard title="Spam rate" value={metrics?.spam_rate ? `${(metrics.spam_rate*100).toFixed(2)}%` : "—"} />
          <MetricCard title="False Positives / day" value={metrics?.false_positives ?? "—"} />
          <MetricCard title="Avg latency (ms)" value={metrics?.avg_latency_ms ?? "—"} />
        </div>

        <section className="mt-6">
          <h3 className="font-medium mb-2">Confidence histogram</h3>
          <ConfidenceHistogram buckets={metrics?.confidence_histogram || []} />
        </section>
      </div>

      <aside className="bg-white p-6 rounded-xl shadow">
        <h3 className="font-semibold mb-3">Models</h3>
        <div className="space-y-3">
          {models.length === 0 ? <div className="text-sm text-slate-500">No models found.</div> : (
            models.map(m => (
              <div key={m.version} className="p-3 border rounded">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">{m.version}</div>
                    <div className="text-xs text-slate-500">{m.created_at}</div>
                  </div>
                  <div className="text-xs text-slate-600">thr: {m.threshold ?? "0.5"}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="p-4 border rounded">
      <div className="text-sm text-slate-500">{title}</div>
      <div className="text-2xl font-semibold mt-2">{value}</div>
    </div>
  );
}

function ConfidenceHistogram({ buckets }) {
  // buckets: [{low, high, count}, ...] or array of counts
  if (!buckets || buckets.length === 0) {
    return <div className="text-sm text-slate-400">No data</div>;
  }
  const total = buckets.reduce((s, b) => s + (b.count ?? b), 0);
  return (
    <div className="flex gap-2 items-end h-36">
      {buckets.map((b, i) => {
        const count = b.count ?? b;
        const h = Math.round((count / (total || 1)) * 100);
        return (
          <div key={i} className="flex-1 text-center">
            <div className="h-full flex items-end">
              <div style={{ height: `${h}%` }} className="w-full bg-sky-400 rounded-t" />
            </div>
            <div className="text-xs mt-2">{((b.low ?? i/10)*100).toFixed(0)}%</div>
          </div>
        );
      })}
    </div>
  );
}
