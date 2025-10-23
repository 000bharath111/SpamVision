// src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import ReviewQueue from "./pages/ReviewQueue";
import ModelManager from "./pages/ModelManager";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-sky-50">
        <header className="max-w-6xl mx-auto p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-lg flex items-center justify-center font-bold">SS</div>
            <div>
              <h1 className="text-xl font-semibold">SMS Spam Platform</h1>
              <div className="text-sm text-slate-500">Hybrid pipeline • Active learning • Monitoring</div>
            </div>
          </div>
          <nav className="flex items-center gap-3 text-sm">
            <Link to="/" className="px-3 py-2 rounded hover:bg-white/60">Home</Link>
            <Link to="/dashboard" className="px-3 py-2 rounded hover:bg-white/60">Dashboard</Link>
            <Link to="/review" className="px-3 py-2 rounded hover:bg-white/60">Review</Link>
            <Link to="/models" className="px-3 py-2 rounded hover:bg-white/60">Models</Link>
            <Link to="/settings" className="px-3 py-2 rounded hover:bg-white/60">Settings</Link>
          </nav>
        </header>

        <main className="max-w-6xl mx-auto p-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/models" element={<ModelManager />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        <footer className="max-w-6xl mx-auto p-4 text-center text-sm text-slate-500">
          © {new Date().getFullYear()} SMS Spam Platform — built for production demos
        </footer>
      </div>
    </BrowserRouter>
  );
}
