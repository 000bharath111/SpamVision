// src/pages/Home.jsx
import React, { useState } from "react";
import PredictForm from "../components/PredictForm";
import ResultCard from "../components/ResultCard";
import SHAPViz from "../components/SHAPViz";

export default function Home() {
  const [result, setResult] = useState(null);
  const [shap, setShap] = useState(null);

  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 bg-white rounded-xl p-6 shadow">
        <h2 className="text-lg font-semibold mb-3">Quick Predict</h2>
        <PredictForm onResult={(r) => { setResult(r); setShap(null); }} onExplain={(r, shapPayload) => { setResult(r); setShap(shapPayload); }} />
        {result && <ResultCard result={result} className="mt-6" />}
      </div>

      <aside className="bg-white rounded-xl p-6 shadow">
        <h3 className="font-semibold mb-2">Model Info</h3>
        <div className="text-sm text-slate-600">Active model version: <span className="font-medium">{result?.model_version ?? "—"}</span></div>
        <div className="mt-4 text-sm text-slate-500">
          This UI sends messages to the backend `/predict` endpoint with an optional threshold override. Use the Explore / Dashboard pages for metrics and review queue.
        </div>

        {shap ? (
          <div className="mt-4">
            <h4 className="font-medium">Explanation</h4>
            <SHAPViz payload={shap} />
          </div>
        ) : null}
      </aside>
    </section>
  );
}
