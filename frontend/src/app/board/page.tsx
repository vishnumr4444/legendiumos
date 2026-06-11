"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Shell from "@/components/Shell";
import { api, currentUser } from "@/lib/api";
import { PriorityDot, STATUS_COLORS, STATUS_LABELS } from "@/components/viz";

const COLUMNS = ["todo", "in_progress", "review", "blocked", "done"];

export default function BoardPage() {
  return <Suspense><Board /></Suspense>;
}

function Board() {
  const params = useSearchParams();
  const [items, setItems] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [filter, setFilter] = useState<number | 0>(0);
  const [open, setOpen] = useState<any>(null);
  const [dragId, setDragId] = useState<number | null>(null);
  const [over, setOver] = useState<string | null>(null);
  const user = currentUser();

  const load = () => {
    api(`/api/work-items${filter ? `?project_id=${filter}` : ""}`).then(setItems).catch(() => {});
    api("/api/projects").then(setProjects).catch(() => {});
  };
  useEffect(() => { load(); }, [filter]);
  useEffect(() => {
    const id = params.get("item");
    if (id) api(`/api/work-items/${id}`).then(setOpen).catch(() => {});
  }, [params]);

  const drop = async (status: string) => {
    setOver(null);
    if (dragId == null) return;
    setItems((arr) => arr.map((i) => (i.id === dragId ? { ...i, status } : i)));
    try { await api(`/api/work-items/${dragId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }); }
    catch { load(); }
    setDragId(null);
  };

  return (
    <Shell>
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4 reveal">
        <div>
          <h1 className="display text-2xl font-bold tracking-wide">Mission Board</h1>
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            {user?.role === "employee" ? "Your tasks only — drag between columns to update status." : "Drag cards to update status. Changes sync to Jira when configured."}
          </p>
        </div>
        <select value={filter} onChange={(e) => setFilter(Number(e.target.value))} className="px-3 py-2 text-sm">
          <option value={0}>All projects</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {COLUMNS.map((col) => {
          const colItems = items.filter((i) => i.status === col);
          return (
            <div key={col}
                 className={`panel kanban-col p-3 min-h-[420px] transition-all ${over === col ? "drag-over" : ""}`}
                 onDragOver={(e) => { e.preventDefault(); setOver(col); }}
                 onDragLeave={() => setOver(null)}
                 onDrop={() => drop(col)}>
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="display text-[11px] font-bold tracking-widest uppercase" style={{ color: STATUS_COLORS[col] }}>{STATUS_LABELS[col]}</span>
                <span className="chip">{colItems.length}</span>
              </div>
              <div className="space-y-2">
                {colItems.map((i) => (
                  <div key={i.id} draggable onDragStart={() => setDragId(i.id)}
                       onClick={() => api(`/api/work-items/${i.id}`).then(setOpen)}
                       className="kanban-card panel panel-hover p-3 text-sm reveal">
                    <div className="flex items-center gap-2 mb-1.5">
                      <PriorityDot p={i.priority} />
                      <span className="chip">{i.type}</span>
                      {i.jira_key && <span className="chip chip-cyan">{i.jira_key}</span>}
                    </div>
                    <div className="leading-snug">{i.title}</div>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-[10px]" style={{ color: "var(--muted)" }}>{i.project_name}</span>
                      {i.assignee && <span className="w-5 h-5 rounded-full grid place-items-center text-[9px] font-bold text-[#04141a]" title={i.assignee} style={{ background: i.assignee_color }}>{i.assignee[0]}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {open && <ItemDrawer item={open} onClose={() => setOpen(null)} onChanged={() => { load(); api(`/api/work-items/${open.id}`).then(setOpen); }} />}
    </Shell>
  );
}

function ItemDrawer({ item, onClose, onChanged }: any) {
  const [body, setBody] = useState("");
  const [posting, setPosting] = useState(false);
  const post = async () => {
    if (!body.trim()) return;
    setPosting(true);
    try {
      const res = await api(`/api/work-items/${item.id}/comments`, { method: "POST", body: JSON.stringify({ body }) });
      setBody(""); onChanged();
      if (res.ai_flags?.length) alert(`AI flagged this comment: ${res.ai_flags.join(", ")}. Leads notified.`);
    } finally { setPosting(false); }
  };
  return (
    <div className="fixed inset-0 z-30 flex justify-end" style={{ background: "rgba(0,0,0,0.45)" }} onClick={onClose}>
      <div className="w-full max-w-md h-full overflow-auto p-6 reveal" style={{ background: "var(--panel)", borderLeft: "1px solid var(--border)" }} onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="chip">{item.type}</span>
          <span className="chip" style={{ color: STATUS_COLORS[item.status], borderColor: STATUS_COLORS[item.status] }}>{STATUS_LABELS[item.status]}</span>
          <span className="chip">{item.priority}</span>
          {item.jira_key && <span className="chip chip-cyan">{item.jira_key}</span>}
        </div>
        <h2 className="display text-lg font-bold mt-3">{item.title}</h2>
        <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>{item.description || "No description."}</p>
        <div className="grid grid-cols-2 gap-2 text-xs mt-4">
          <Info k="Project" v={item.project_name} />
          <Info k="Assignee" v={item.assignee || "Unassigned"} />
          <Info k="Discipline" v={item.discipline} />
          <Info k="Estimate" v={`${item.estimate_hours}h · ${item.logged_hours}h logged`} />
          {item.due_date && <Info k="Due" v={new Date(item.due_date).toLocaleDateString()} />}
        </div>
        {item.children?.length > 0 && (
          <div className="mt-4">
            <div className="display text-[11px] font-bold tracking-widest uppercase mb-2">Children</div>
            {item.children.map((c: any) => (
              <div key={c.id} className="text-xs py-1 flex gap-2 items-center"><span className="chip">{c.type}</span>{c.title}</div>
            ))}
          </div>
        )}
        <div className="mt-5">
          <div className="display text-[11px] font-bold tracking-widest uppercase mb-2">Comments · AI-scanned</div>
          <div className="space-y-2">
            {item.comments?.map((c: any) => (
              <div key={c.id} className="p-3 rounded-xl text-xs" style={{ background: "var(--panel2)", border: "1px solid var(--border)" }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="w-4 h-4 rounded-full" style={{ background: c.author_color }} />
                  <b>{c.author}</b>
                  <span style={{ color: "var(--muted)" }}>{new Date(c.created_at).toLocaleString()}</span>
                </div>
                {c.ai_flags?.filter(Boolean).length > 0 && (
                  <div className="flex gap-1 mb-1">{c.ai_flags.filter(Boolean).map((f: string) => <span key={f} className="chip chip-danger">{f}</span>)}</div>
                )}
                {c.body}
              </div>
            ))}
          </div>
          <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={2} placeholder="Add a comment — AI scans for blockers, risks, urgency…" className="w-full p-3 text-sm mt-3" />
          <button onClick={post} disabled={posting} className="btn-primary px-4 py-2 text-sm mt-2">{posting ? "Posting…" : "Comment"}</button>
        </div>
      </div>
    </div>
  );
}
function Info({ k, v }: { k: string; v: string }) {
  return (
    <div className="p-2 rounded-lg" style={{ background: "var(--panel2)" }}>
      <div style={{ color: "var(--muted)" }}>{k}</div>
      <div className="font-semibold mt-0.5">{v}</div>
    </div>
  );
}
