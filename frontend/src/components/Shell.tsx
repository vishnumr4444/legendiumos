"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTheme } from "@/lib/theme";
import { api, currentUser, logout } from "@/lib/api";

const NAV = [
  { href: "/", label: "Dashboard", icon: "◧", roles: ["admin", "lead", "employee"] },
  { href: "/command", label: "AI Command", icon: "⌬", roles: ["admin", "lead"] },
  { href: "/board", label: "Board", icon: "▤", roles: ["admin", "lead", "employee"] },
  { href: "/workload", label: "Workload", icon: "⫛", roles: ["admin", "lead"] },
  { href: "/reports", label: "Reports", icon: "≣", roles: ["admin", "lead"] },
  { href: "/knowledge", label: "Knowledge", icon: "✦", roles: ["admin", "lead", "employee"] },
];

export default function Shell({ children }: { children: React.ReactNode }) {
  const { night, toggle } = useTheme();
  const path = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [notes, setNotes] = useState<any[]>([]);
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    const u = currentUser();
    if (!u) { router.push("/login"); return; }
    setUser(u);
    api("/api/dashboard/notifications").then(setNotes).catch(() => {});
  }, [router]);

  const stars = useMemo(
    () => Array.from({ length: 50 }, (_, i) => ({
      left: `${(i * 37) % 100}%`, top: `${(i * 53) % 100}%`,
      size: 1 + (i % 3), delay: `${(i % 10) * 0.4}s`,
    })), []);

  if (!user) return null;
  const unread = notes.filter((n) => !n.read).length;

  return (
    <div className="min-h-screen relative">
      <div className="starfield">
        {stars.map((s, i) => (
          <span key={i} className="star" style={{ left: s.left, top: s.top, width: s.size, height: s.size, animationDelay: s.delay }} />
        ))}
      </div>

      <aside className="fixed left-0 top-0 bottom-0 w-56 z-20 hidden md:flex flex-col p-4 gap-1"
             style={{ background: "var(--panel)", borderRight: "1px solid var(--border)" }}>
        <img src={night ? "/logo-night.png" : "/logo-day-transparent.png"} alt="Legendium" className="h-9 object-contain object-left mb-1 transition-opacity" />
        <div className="flex items-center gap-2 mb-5 pl-0.5">
          <span className="eyes"><i /><i /></span>
          <span className="display text-[10px] tracking-[0.3em]" style={{ color: "var(--muted)" }}>OS · v1.0</span>
        </div>
        {NAV.filter((n) => n.roles.includes(user.role)).map((n) => (
          <Link key={n.href} href={n.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all ${path === n.href ? "btn-primary" : "btn-ghost border-transparent"}`}>
            <span className="text-base leading-none">{n.icon}</span>{n.label}
          </Link>
        ))}
        <div className="mt-auto panel p-3 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-full grid place-items-center font-bold text-[#04141a]" style={{ background: user.avatar_color }}>
              {user.full_name[0]}
            </span>
            <div>
              <div className="font-semibold text-[13px]">{user.full_name}</div>
              <div style={{ color: "var(--muted)" }}>{user.role === "admin" ? "Master Admin" : user.role === "lead" ? "Team Lead" : "Team Member"}</div>
            </div>
          </div>
          <button onClick={logout} className="btn-ghost w-full mt-3 py-1.5 text-xs">Sign out</button>
        </div>
      </aside>

      <header className="fixed top-0 left-0 md:left-56 right-0 z-10 flex items-center justify-between px-5 h-14"
              style={{ background: "color-mix(in srgb, var(--bg) 80%, transparent)", backdropFilter: "blur(10px)", borderBottom: "1px solid var(--border)" }}>
        <div className="display text-xs tracking-[0.25em]" style={{ color: "var(--muted)" }}>
          {night ? "NIGHT OPS // LEGENDIUM UNIVERSE" : "DAY OPS // LEGENDIUM HQ"}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowNotes((s) => !s)} className="btn-ghost px-3 py-1.5 text-sm relative">
            ◉ {unread > 0 && <span className="absolute -top-1 -right-1 text-[10px] px-1.5 rounded-full font-bold" style={{ background: "var(--cyan)", color: "#04141a" }}>{unread}</span>}
          </button>
          <button onClick={toggle} className="btn-ghost px-3 py-1.5 text-sm" title="Switch identity">
            {night ? "☾ Night" : "☀ Day"}
          </button>
        </div>
        {showNotes && (
          <div className="absolute right-4 top-14 w-80 panel p-2 max-h-96 overflow-auto reveal">
            {notes.length === 0 && <div className="p-3 text-sm" style={{ color: "var(--muted)" }}>No notifications yet. The AI will post here when something needs you.</div>}
            {notes.map((n) => (
              <div key={n.id} className="p-2.5 text-xs rounded-lg flex gap-2 items-start" style={{ borderBottom: "1px solid var(--border)" }}>
                <span className={`chip ${n.kind === "risk" ? "chip-danger" : n.kind === "approval" ? "chip-warn" : n.kind === "assignment" ? "chip-cyan" : ""}`}>{n.kind}</span>
                <span>{n.message}</span>
              </div>
            ))}
          </div>
        )}
      </header>

      <main className="md:pl-56 pt-14 relative z-[1]">
        <div className="p-5 max-w-[1500px] mx-auto">{children}</div>
      </main>
    </div>
  );
}
