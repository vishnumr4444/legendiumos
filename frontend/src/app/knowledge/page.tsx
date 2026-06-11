"use client";
import { useEffect, useRef, useState } from "react";
import Shell from "@/components/Shell";
import { api, API, token, currentUser } from "@/lib/api";

export default function Knowledge() {
  const [docs, setDocs] = useState<any[]>([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const user = currentUser();
  const canUpload = user?.role === "admin" || user?.role === "lead";

  const load = () => api("/api/knowledge").then(setDocs).catch(() => {});
  useEffect(() => { load(); }, []);

  const upload = async (file: File) => {
    setBusy(true); setNote("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API}/api/knowledge/upload`, {
        method: "POST", headers: { Authorization: `Bearer ${token()}` }, body: fd,
      });
      const data = await res.json();
      setNote(data.note || "Uploaded.");
      load();
    } finally { setBusy(false); }
  };

  return (
    <Shell>
      <div className="reveal mb-5">
        <h1 className="display text-2xl font-bold tracking-wide">Knowledge Base</h1>
        <p className="text-sm" style={{ color: "var(--muted)" }}>SOPs, roadmaps, vendor docs. Text files are indexed and fed to the AI Command Center as planning context.</p>
      </div>
      {canUpload && (
        <div className="panel scan p-6 mb-4 text-center reveal cursor-pointer" onClick={() => fileRef.current?.click()}
             onDragOver={(e) => e.preventDefault()}
             onDrop={(e) => { e.preventDefault(); if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]); }}>
          <input ref={fileRef} type="file" className="hidden" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
          <span className="eyes"><i /><i /></span>
          <div className="text-sm mt-2">{busy ? "Uploading…" : "Drop a document here, or click to browse"}</div>
          <div className="text-[11px] mt-1" style={{ color: "var(--muted)" }}>.txt .md .csv .json index instantly · binary formats stored for the extraction pipeline</div>
        </div>
      )}
      {note && <div className="panel p-3 text-xs mb-4" style={{ color: "var(--cyan)" }}>{note}</div>}
      <div className="panel p-5 reveal">
        <div className="display text-sm font-bold tracking-widest uppercase mb-3">Library</div>
        {docs.length === 0 && <div className="text-sm py-4" style={{ color: "var(--muted)" }}>Empty. Upload your first SOP or roadmap to give the AI memory.</div>}
        <div className="space-y-2">
          {docs.map((d) => (
            <div key={d.id} className="flex items-center gap-3 p-2.5 rounded-xl text-sm" style={{ border: "1px solid var(--border)" }}>
              <span className="chip chip-cyan">{d.kind}</span>
              <span className="flex-1 truncate">{d.filename}</span>
              <span className="text-[11px]" style={{ color: "var(--muted)" }}>{(d.size_bytes / 1024).toFixed(1)} KB · {new Date(d.uploaded_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </div>
    </Shell>
  );
}
