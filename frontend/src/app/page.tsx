"use client";
import { useState } from "react";
import { apiGet, API_BASE } from "../lib/fetcher";

export default function Home() {
  const [status, setStatus] = useState<string>("");

  return (
    <div className="container">
      <h1>MedAssist-AI</h1>
      <p>Frontend → FastAPI at <code>{API_BASE}</code></p>
      <div className="row" style={{marginTop:"1rem"}}>
        <a className="button" href="/dashboard">Open Dashboard</a>
        <button className="button" onClick={async () => {
          try { setStatus(JSON.stringify(await apiGet("/api/v1/health"))); }
          catch (e:any) { setStatus(e.message); }
        }}>Ping /health</button>
      </div>
      <pre className="card" style={{marginTop:"1rem"}}>{status || "Click Ping /health"}</pre>
    </div>
  );
}
