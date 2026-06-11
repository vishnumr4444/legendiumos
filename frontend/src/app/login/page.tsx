"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "@/lib/theme";
import { login } from "@/lib/api";

const DEMO = [
  { u: "joseph", label: "Joseph · Master Admin" },
  { u: "amal", label: "Amal · VR/XR Lead" },
  { u: "anson", label: "Anson · Robotics Lead" },
  { u: "noel", label: "Noel · 3D Artist" },
  { u: "vishnu", label: "Vishnu · Web & UI/UX" },
  { u: "krishnaprasad", label: "Krishnaprasad · Backend" },
  { u: "vysakh", label: "Vysakh · QC & Assembly" },
];

export default function Login() {
  const { night, toggle } = useTheme();
  const router = useRouter();
  const [username, setUsername] = useState("joseph");
  const [password, setPassword] = useState("legendium");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const go = async (u?: string) => {
    setBusy(true); setErr("");
    try {
      await login(u || username, u ? "legendium" : password);
      router.push("/");
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <button onClick={toggle} className="btn-ghost px-3 py-1.5 text-sm fixed top-4 right-4">
        {night ? "☾ Night" : "☀ Day"}
      </button>
      <div className="w-full max-w-md panel scan p-8 reveal">
        <img src={night ? "/logo-night.png" : "/logo-day-transparent.png"} alt="Legendium" className="h-12 object-contain mx-auto" />
        <div className="flex items-center justify-center gap-2 mt-3 mb-8">
          <span className="eyes"><i /><i /></span>
          <span className="display text-[11px] tracking-[0.35em]" style={{ color: "var(--muted)" }}>OPERATING SYSTEM</span>
        </div>
        <form onSubmit={(e) => { e.preventDefault(); go(); }} className="space-y-3">
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" className="w-full px-4 py-3 text-sm" autoFocus />
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" className="w-full px-4 py-3 text-sm" />
          {err && <div className="text-sm" style={{ color: "var(--danger)" }}>{err}</div>}
          <button disabled={busy} className="btn-primary w-full py-3 text-sm">{busy ? "Authenticating…" : "Enter Legendium OS"}</button>
        </form>
        <div className="mt-6">
          <div className="text-[11px] mb-2 tracking-widest display" style={{ color: "var(--muted)" }}>DEMO CREW · password "legendium"</div>
          <div className="flex flex-wrap gap-1.5">
            {DEMO.map((d) => (
              <button key={d.u} onClick={() => go(d.u)} className="chip chip-cyan hover:opacity-80">{d.label}</button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
