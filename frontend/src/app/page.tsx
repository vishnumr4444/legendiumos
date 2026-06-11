"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Shell from "@/components/Shell";
import { api } from "@/lib/api";
import { CountUp, Ring, LoadBar, StatusChip, PriorityDot } from "@/components/viz";

export default function Dashboard() {
  const [d, setD] = useState<any>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api("/api/dashboard").then(setD).catch((e) => setErr(e.message)); }, []);

  return (
    <Shell>
      {err && <div className="panel p-4 text-sm" style={{ color: "var(--danger)" }}>API unreachable: {err}. Start the backend (uvicorn app.main:app).</div>}
      {!d && !err && <Thinking label="Assembling your dashboard" />}
      {d?.view === "executive" && <Executive d={d} />}
      {d?.view === "lead" && <Lead d={d} />}
      {d?.view === "employee" && <Employee d={d} />}
    </Shell>
  );
}

function Thinking({ label }: { label: string }) {
  return (
    <div className="h-64 grid place-items-center">
      <div className="flex flex-col items-center gap-3">
        <span className="eyes thinking"><i /><i /></span>
        <span className="text-sm" style={{ color: "var(--muted)" }}>{label}…</span>
      </div>
    </div>
  );
}

function Kpi({ label, value, suffix, accent }: any) {
  return (
    <div className="panel panel-hover p-4 reveal">
      <div className="text-[11px] tracking-widest uppercase mb-1" style={{ color: "var(--muted)" }}>{label}</div>
      <CountUp value={value} suffix={suffix} className="text-3xl font-bold" />
      {accent && <div className="text-[11px] mt-1" style={{ color: "var(--muted)" }}>{accent}</div>}
    </div>
  );
}

/* ----------------------------- EXECUTIVE (Joseph) ----------------------------- */
function Executive({ d }: { d: any }) {
  const k = d.kpis;
  return (
    <div className="space-y-5">
      <Header title="Mission Control" sub="Every department, every project, every signal." />
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <Kpi label="Open items" value={k.open_items} />
        <Kpi label="Blocked" value={k.blocked} accent="needs attention" />
        <Kpi label="Done" value={k.done_this_sprint} />
        <Kpi label="Burn rate" value={k.burn_rate} suffix="%" accent={`${k.logged_hours}h of ${k.scope_hours}h`} />
        <Kpi label="Crew" value={d.workload.length} accent="across 3 departments" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {d.departments.map((dept: any, i: number) => (
          <div key={dept.id} className="panel panel-hover scan p-5 reveal" style={{ animationDelay: `${i * 0.08}s` }}>
            <div className="flex justify-between items-start">
              <div>
                <div className="display font-bold tracking-wider">{dept.name}</div>
                <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>{dept.headcount} crew · {dept.velocity_14d}h velocity / 14d</div>
              </div>
              <Ring pct={dept.completion} size={72} />
            </div>
            <div className="flex gap-2 mt-3">
              <span className="chip chip-cyan">{dept.open} open</span>
              <span className="chip chip-ok">{dept.done} done</span>
              {dept.blocked > 0 && <span className="chip chip-danger">{dept.blocked} blocked</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-5 gap-4">
        <div className="panel p-5 lg:col-span-3 reveal">
          <SectionTitle title="Project health" sub="progress to target" />
          <div className="space-y-3 mt-3 max-h-[340px] overflow-auto pr-1">
            {d.projects.map((p: any) => (
              <div key={p.id} className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: p.health === "green" ? "var(--ok)" : p.health === "amber" ? "var(--warn)" : "var(--danger)", boxShadow: "0 0 6px currentColor" }} />
                <div className="w-44 truncate text-sm">{p.name}</div>
                <div className="flex-1"><LoadBar pct={p.progress} color="var(--cyan)" /></div>
                <div className="w-20 text-right text-xs" style={{ color: "var(--muted)" }}>{p.open_items} open</div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-5 lg:col-span-2 reveal">
          <SectionTitle title="AI risk feed" sub="flagged from comments" />
          <div className="space-y-2.5 mt-3 max-h-[340px] overflow-auto pr-1">
            {d.risk_feed.map((r: any) => (
              <div key={r.id} className="p-3 rounded-xl text-xs" style={{ background: "var(--panel2)", border: "1px solid var(--border)" }}>
                <div className="flex gap-1.5 mb-1.5 flex-wrap">
                  {r.flags.map((f: string) => <span key={f} className={`chip ${f === "blocker" || f === "urgent" ? "chip-danger" : "chip-warn"}`}>{f}</span>)}
                </div>
                <div className="font-semibold mb-0.5">{r.item}</div>
                <div style={{ color: "var(--muted)" }}>{r.author}: {r.body}</div>
              </div>
            ))}
            {d.risk_feed.length === 0 && <Empty text="No risks flagged. The eyes are watching." />}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <WorkloadPanel workload={d.workload} />
        <UpcomingPanel items={d.upcoming} />
      </div>
    </div>
  );
}

/* ------------------------------- LEAD (Amal / Anson) ------------------------------- */
function Lead({ d }: { d: any }) {
  const k = d.kpis;
  return (
    <div className="space-y-5">
      <Header title="Team Command" sub={d.sprint ? `${d.sprint.name} · ends ${new Date(d.sprint.end_date).toLocaleDateString()}` : "Your department at a glance."} />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Kpi label="Team open" value={k.team_open} />
        <Kpi label="Blocked" value={k.blocked} />
        <Kpi label="Pending approvals" value={k.pending_approvals} accent="in review" />
        <div className="panel panel-hover p-4 reveal flex items-center justify-between">
          <div>
            <div className="text-[11px] tracking-widest uppercase" style={{ color: "var(--muted)" }}>Sprint</div>
            <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>progress</div>
          </div>
          <Ring pct={k.sprint_progress} size={64} />
        </div>
      </div>
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="panel p-5 reveal">
          <SectionTitle title="Awaiting your approval" sub="items in review" />
          <ItemList items={d.approvals} empty="Nothing in review. Smooth sailing." />
        </div>
        <div className="panel p-5 reveal">
          <SectionTitle title="Blocked" sub="unblock these first" />
          <ItemList items={d.blocked_items} empty="No blockers in your team." />
        </div>
      </div>
      <div className="grid lg:grid-cols-2 gap-4">
        <WorkloadPanel workload={d.workload} />
        <UpcomingPanel items={d.upcoming} />
      </div>
    </div>
  );
}

/* ------------------------------- EMPLOYEE ------------------------------- */
function Employee({ d }: { d: any }) {
  const k = d.kpis;
  return (
    <div className="space-y-5">
      <Header title="Your Missions" sub="Only your assigned work appears here." />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Kpi label="Open tasks" value={k.my_open} />
        <Kpi label="Due this week" value={k.due_this_week} />
        <Kpi label="In review" value={k.in_review} />
        <div className="panel panel-hover p-4 reveal flex items-center justify-between">
          <div>
            <div className="text-[11px] tracking-widest uppercase" style={{ color: "var(--muted)" }}>Personal KPI</div>
            <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>{d.logged_hours}h logged</div>
          </div>
          <Ring pct={k.completion_rate} size={64} label="done" />
        </div>
      </div>
      <div className="panel p-5 reveal">
        <SectionTitle title="Assigned to you" sub="sorted by due date" />
        <ItemList items={d.my_items} empty="No open tasks. Your lead will assign new missions." />
      </div>
      <div className="panel p-5 reveal">
        <SectionTitle title="Completed" sub="recent wins" />
        <ItemList items={d.completed} empty="Completed work lands here." />
      </div>
    </div>
  );
}

/* ------------------------------- shared bits ------------------------------- */
function Header({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="reveal">
      <h1 className="display text-2xl font-bold tracking-wide flex items-center gap-3">
        {title} <span className="eyes"><i /><i /></span>
      </h1>
      <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>{sub}</p>
    </div>
  );
}
function SectionTitle({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="flex items-baseline gap-2">
      <h2 className="display text-sm font-bold tracking-widest uppercase">{title}</h2>
      {sub && <span className="text-[11px]" style={{ color: "var(--muted)" }}>{sub}</span>}
    </div>
  );
}
function Empty({ text }: { text: string }) {
  return <div className="text-sm py-6 text-center" style={{ color: "var(--muted)" }}>{text}</div>;
}
function ItemList({ items, empty }: { items: any[]; empty: string }) {
  if (!items?.length) return <Empty text={empty} />;
  return (
    <div className="space-y-2 mt-3">
      {items.map((i: any) => (
        <Link key={i.id} href={`/board?item=${i.id}`} className="flex items-center gap-3 p-2.5 rounded-xl transition-colors hover:bg-[var(--panel2)]" style={{ border: "1px solid var(--border)" }}>
          <PriorityDot p={i.priority} />
          <span className="chip">{i.type}</span>
          <span className="text-sm flex-1 truncate">{i.title}</span>
          <span className="hidden sm:block text-[11px] w-28 truncate" style={{ color: "var(--muted)" }}>{i.project}</span>
          {i.due_date && <span className="text-[11px] w-16 text-right" style={{ color: "var(--muted)" }}>{new Date(i.due_date).toLocaleDateString(undefined, { day: "numeric", month: "short" })}</span>}
          <StatusChip status={i.status} />
        </Link>
      ))}
    </div>
  );
}
function WorkloadPanel({ workload }: { workload: any[] }) {
  return (
    <div className="panel p-5 reveal">
      <SectionTitle title="Crew load" sub="remaining estimate vs weekly capacity" />
      <div className="space-y-3 mt-3">
        {workload.map((w: any) => (
          <div key={w.user_id} className="flex items-center gap-3">
            <span className="w-7 h-7 rounded-full grid place-items-center text-xs font-bold shrink-0 text-[#04141a]" style={{ background: w.avatar_color }}>{w.full_name[0]}</span>
            <div className="w-28 truncate text-sm">{w.full_name}</div>
            <div className="flex-1"><LoadBar pct={w.utilization} /></div>
            <div className="w-14 text-right text-xs display">{w.utilization}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
function UpcomingPanel({ items }: { items: any[] }) {
  return (
    <div className="panel p-5 reveal">
      <SectionTitle title="Coming up" sub="next due across visible scope" />
      <ItemList items={items} empty="No dated items ahead." />
    </div>
  );
}
