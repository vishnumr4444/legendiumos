"use client";
import { useState } from "react";
import Shell from "@/components/Shell";
import { API, token } from "@/lib/api";

const KINDS = [
  { k: "daily", label: "Daily standup", desc: "What moved in the last 24h, by person and project." },
  { k: "weekly", label: "Weekly summary", desc: "Progress, completions and blockers across the week." },
  { k: "sprint", label: "Sprint report", desc: "Scope, burn and carry-over for the active sprint." },
  { k: "executive", label: "Executive brief", desc: "Cross-department status for leadership review." },
];

export default function Reports() {
  const [busy, setBusy] = useState("");
  const download = async (kind: string, format: string) => {
    setBusy(kind + format);
    try {
      const res = await fetch(`${API}/api/reports/${kind}?format=${format}`, { headers: { Authorization: `Bearer ${token()}` } });
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `legendium-${kind}.${format === "md" ? "md" : format === "csv" ? "csv" : "json"}`;
      a.click();
    } finally { setBusy(""); }
  };
  return (
    <Shell>
      <div className="reveal mb-5">
        <h1 className="display text-2xl font-bold tracking-wide">Reports</h1>
        <p className="text-sm" style={{ color: "var(--muted)" }}>Generated live from current data, scoped to what you're allowed to see.</p>
      </div>
      <div className="grid sm:grid-cols-2 gap-4">
        {KINDS.map((r, i) => (
          <div key={r.k} className="panel panel-hover p-5 reveal" style={{ animationDelay: `${i * 0.07}s` }}>
            <div className="display font-bold">{r.label}</div>
            <p className="text-xs mt-1 mb-4" style={{ color: "var(--muted)" }}>{r.desc}</p>
            <div className="flex gap-2">
              {["csv", "md", "json"].map((f) => (
                <button key={f} onClick={() => download(r.k, f)} disabled={busy === r.k + f} className="btn-ghost px-4 py-1.5 text-xs uppercase">
                  {busy === r.k + f ? "…" : f}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Shell>
  );
}
