"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { api } from "@/lib/api";
import { LoadBar, CountUp } from "@/components/viz";

export default function Workload() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  const [applied, setApplied] = useState<number[]>([]);

  const load = () => api("/api/workload").then(setData).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);

  const apply = async (s: any) => {
    await api(`/api/workload/reassign/${s.work_item_id}/${s.to_user_id}`, { method: "POST" });
    setApplied((a) => [...a, s.work_item_id]);
    load();
  };

  return (
    <Shell>
      <div className="reveal mb-5">
        <h1 className="display text-2xl font-bold tracking-wide">Workload Engine</h1>
        <p className="text-sm" style={{ color: "var(--muted)" }}>Remaining estimates vs weekly capacity. The AI proposes rebalances when someone runs hot.</p>
      </div>
      {err && <div className="panel p-4 text-sm" style={{ color: "var(--danger)" }}>{err}</div>}
      {data && (
        <div className="space-y-5">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {data.team.map((w: any, i: number) => (
              <div key={w.user_id} className="panel panel-hover scan p-4 reveal" style={{ animationDelay: `${i * 0.06}s` }}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="w-10 h-10 rounded-full grid place-items-center font-bold text-[#04141a]" style={{ background: w.avatar_color }}>{w.full_name[0]}</span>
                  <div className="min-w-0">
                    <div className="font-semibold text-sm truncate">{w.full_name}</div>
                    <div className="text-[11px] truncate" style={{ color: "var(--muted)" }}>{w.title}</div>
                  </div>
                </div>
                <div className="flex items-end justify-between mb-1.5">
                  <CountUp value={w.utilization} suffix="%" className="text-2xl font-bold" />
                  <span className={`chip ${w.status === "overloaded" ? "chip-danger" : w.status === "high" ? "chip-warn" : w.status === "available" ? "chip-ok" : "chip-cyan"}`}>{w.status}</span>
                </div>
                <LoadBar pct={w.utilization} />
                <div className="text-[11px] mt-2 flex justify-between" style={{ color: "var(--muted)" }}>
                  <span>{w.load_hours}h / {w.capacity_hours}h</span><span>{w.open_items} open</span>
                </div>
              </div>
            ))}
          </div>

          <div className="panel p-5 reveal">
            <h2 className="display text-sm font-bold tracking-widest uppercase mb-1">AI rebalance suggestions</h2>
            <p className="text-xs mb-3" style={{ color: "var(--muted)" }}>Skill-matched moves from overloaded to available crew. One click to apply.</p>
            {data.suggestions.length === 0 && <div className="text-sm py-4" style={{ color: "var(--muted)" }}>Load is balanced. No moves suggested.</div>}
            <div className="space-y-2">
              {data.suggestions.map((s: any, i: number) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-xl flex-wrap" style={{ background: "var(--panel2)", border: "1px solid var(--border)" }}>
                  <div className="flex-1 min-w-[220px]">
                    <div className="text-sm font-semibold">{s.title}</div>
                    <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>{s.reason}</div>
                  </div>
                  <span className="chip chip-warn">{s.from_user}</span>
                  <span style={{ color: "var(--cyan)" }}>→</span>
                  <span className="chip chip-ok">{s.to_user}</span>
                  {applied.includes(s.work_item_id)
                    ? <span className="chip chip-ok">applied</span>
                    : <button onClick={() => apply(s)} className="btn-primary px-4 py-1.5 text-xs">Apply</button>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </Shell>
  );
}
