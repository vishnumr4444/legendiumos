"use client";
import { useState } from "react";
import Shell from "@/components/Shell";
import { api } from "@/lib/api";
import { CountUp } from "@/components/viz";

const SUGGESTIONS = [
  "Launch Chapter 3 with Nano integration, Flipkart listing, and website release.",
  "Create Chapter 4.",
  "Launch Ninja Robot.",
  "Prepare Flipkart Listing.",
  "Create PCB Production Pipeline.",
  "Design Marketing Campaign for Otto.",
];

export default function Command() {
  const [prompt, setPrompt] = useState("");
  const [plan, setPlan] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [err, setErr] = useState("");

  const preview = async (p?: string) => {
    const q = p || prompt;
    if (!q.trim()) return;
    setPrompt(q); setBusy(true); setErr(""); setResult(null); setPlan(null);
    try { setPlan(await api("/api/command/preview", { method: "POST", body: JSON.stringify({ prompt: q }) })); }
    catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  };

  const execute = async () => {
    setExecuting(true); setErr("");
    try {
      setResult(await api("/api/command/execute", { method: "POST", body: JSON.stringify({ prompt, plan }) }));
      setPlan(null);
    } catch (e: any) { setErr(e.message); } finally { setExecuting(false); }
  };

  return (
    <Shell>
      <div className="max-w-4xl mx-auto space-y-5">
        <div className="text-center pt-6 reveal">
          <div className="flex justify-center mb-3"><span className={`eyes ${busy ? "thinking" : ""}`} style={{ transform: "scale(2)" }}><i /><i /></span></div>
          <h1 className="display text-2xl font-bold tracking-wide">AI Command Center</h1>
          <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            Describe the mission. Legendium OS plans epics, stories, tasks, owners, estimates and dependencies — then pushes to Jira.
          </p>
        </div>

        <div className="panel scan p-4 reveal">
          <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={3}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) preview(); }}
            placeholder='e.g. "Launch Chapter 3 with Nano integration, Flipkart listing, and website release."'
            className="w-full p-4 text-sm resize-none" />
          <div className="flex justify-between items-center mt-2">
            <span className="text-[11px]" style={{ color: "var(--muted)" }}>Ctrl/⌘ + Enter to plan</span>
            <button onClick={() => preview()} disabled={busy || !prompt.trim()} className="btn-primary px-6 py-2.5 text-sm disabled:opacity-50">
              {busy ? "Decomposing…" : "Plan it"}
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5 justify-center reveal">
          {SUGGESTIONS.map((s) => <button key={s} onClick={() => preview(s)} className="chip chip-cyan hover:opacity-75">{s}</button>)}
        </div>

        {err && <div className="panel p-4 text-sm" style={{ color: "var(--danger)" }}>{err}</div>}

        {result && (
          <div className="panel p-6 text-center reveal" style={{ borderColor: "var(--ok)" }}>
            <div className="display text-lg font-bold" style={{ color: "var(--ok)" }}>Mission deployed</div>
            <div className="text-sm mt-2" style={{ color: "var(--muted)" }}>
              {result.items_created} work items and {result.dependencies_linked} dependencies created in "{result.project}".
              Owners notified. {result.jira_synced ? "Synced to Jira." : "Jira sync is idle — add JIRA_* keys in backend .env to push tickets."}
            </div>
          </div>
        )}

        {plan && (
          <div className="space-y-4">
            <div className="panel p-5 reveal">
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 text-center">
                {Object.entries({ Epics: plan.totals.epics, Stories: plan.totals.stories, Tasks: plan.totals.tasks, Subtasks: plan.totals.subtasks, Deps: plan.totals.dependencies, Hours: plan.totals.estimate_hours }).map(([k, v]: any) => (
                  <div key={k}>
                    <CountUp value={v} className="text-2xl font-bold" />
                    <div className="text-[11px] uppercase tracking-widest" style={{ color: "var(--muted)" }}>{k}</div>
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between mt-4 pt-4 flex-wrap gap-2" style={{ borderTop: "1px solid var(--border)" }}>
                <div className="text-xs" style={{ color: "var(--muted)" }}>
                  Engine: <span className="chip chip-cyan">{plan.engine}</span> · Project: <b style={{ color: "var(--text)" }}>{plan.project}</b> · Dept: {plan.department}
                </div>
                <button onClick={execute} disabled={executing} className="btn-primary px-6 py-2.5 text-sm">
                  {executing ? "Deploying…" : "Approve & push to Jira →"}
                </button>
              </div>
            </div>

            {plan.epics.map((epic: any, ei: number) => (
              <div key={ei} className="panel p-5 reveal" style={{ animationDelay: `${ei * 0.12}s` }}>
                <div className="flex items-center gap-2">
                  <span className="chip" style={{ color: "var(--accent2)", borderColor: "var(--accent2)" }}>EPIC</span>
                  <span className="display font-bold">{epic.title}</span>
                </div>
                <p className="text-xs mt-1 mb-3" style={{ color: "var(--muted)" }}>{epic.description}</p>
                {epic.stories?.map((story: any, si: number) => (
                  <div key={si} className="ml-3 pl-4 py-2 reveal" style={{ borderLeft: "2px solid var(--border)", animationDelay: `${ei * 0.12 + si * 0.08}s` }}>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="chip chip-cyan">STORY</span>
                      <span className="text-sm font-semibold">{story.title}</span>
                      <span className="chip">{story.owner}</span>
                      <span className="chip">{story.estimate_hours}h</span>
                    </div>
                    {story.tasks?.map((task: any, ti: number) => (
                      <div key={ti} className="ml-3 mt-2 pl-4 reveal" style={{ borderLeft: "2px dashed var(--border)", animationDelay: `${ei * 0.12 + si * 0.08 + ti * 0.05}s` }}>
                        <div className="flex items-center gap-2 text-sm flex-wrap">
                          <span className="eyes" style={{ transform: "scale(0.7)" }}><i /><i /></span>
                          {task.title}
                          <span className="chip">{task.discipline}</span>
                          <span className="chip">{task.owner} · {task.estimate_hours}h</span>
                        </div>
                        {task.subtasks?.map((st: any, sti: number) => (
                          <div key={sti} className="ml-7 mt-1 text-xs flex gap-2 items-center" style={{ color: "var(--muted)" }}>
                            ▪ {st.title} <span className="chip">{st.owner} · {st.estimate_hours}h</span>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ))}

            {plan.dependencies?.length > 0 && (
              <div className="panel p-5 reveal">
                <div className="display text-sm font-bold tracking-widest uppercase mb-3">Dependency chain</div>
                {plan.dependencies.map((dep: any, i: number) => (
                  <div key={i} className="text-xs py-1.5 flex items-center gap-2 flex-wrap">
                    <span className="chip chip-warn">{dep.blocker}</span>
                    <span style={{ color: "var(--cyan)" }}>──blocks──▶</span>
                    <span className="chip">{dep.blocked}</span>
                  </div>
                ))}
              </div>
            )}

            {plan.milestones?.length > 0 && (
              <div className="panel p-5 reveal">
                <div className="display text-sm font-bold tracking-widest uppercase mb-4">Milestones</div>
                <div className="flex items-center">
                  {plan.milestones.map((m: any, i: number) => (
                    <div key={i} className="flex items-center flex-1 last:flex-none">
                      <div className="flex flex-col items-center text-center">
                        <span className="w-3 h-3 rounded-full" style={{ background: "var(--cyan)", boxShadow: "0 0 10px var(--cyan)" }} />
                        <span className="text-xs mt-2 font-semibold whitespace-nowrap">{m.name}</span>
                        <span className="text-[10px]" style={{ color: "var(--muted)" }}>+{m.offset_days}d</span>
                      </div>
                      {i < plan.milestones.length - 1 && <div className="flex-1 h-px mx-2 mb-7" style={{ background: "var(--border)" }} />}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Shell>
  );
}
