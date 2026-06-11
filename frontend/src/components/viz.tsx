"use client";
import { useEffect, useRef, useState } from "react";

/** Animated count-up number in the display face. */
export function CountUp({ value, suffix = "", className = "" }: { value: number; suffix?: string; className?: string }) {
  const [v, setV] = useState(0);
  useEffect(() => {
    let raf: number; const start = performance.now();
    const tick = (t: number) => {
      const p = Math.min((t - start) / 800, 1);
      setV(Math.round(value * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <span className={`display ${className}`}>{v}{suffix}</span>;
}

/** SVG progress ring with glow. */
export function Ring({ pct, size = 86, label, color = "var(--cyan)" }: { pct: number; size?: number; label?: string; color?: string }) {
  const r = (size - 12) / 2;
  const c = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--ring-track)" strokeWidth="8" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="8"
              strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - Math.min(pct, 100) / 100)}
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
              style={{ transition: "stroke-dashoffset 1s cubic-bezier(.2,.8,.2,1)", filter: "drop-shadow(0 0 4px " + color + ")" }} />
      <text x="50%" y="48%" textAnchor="middle" dominantBaseline="central" fill="var(--text)"
            style={{ font: "700 15px var(--font-display)" }}>{Math.round(pct)}%</text>
      {label && <text x="50%" y="68%" textAnchor="middle" fill="var(--muted)" style={{ font: "10px var(--font-body)" }}>{label}</text>}
    </svg>
  );
}

/** Animated horizontal utilization bar. */
export function LoadBar({ pct, color }: { pct: number; color?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) requestAnimationFrame(() => { if (ref.current) ref.current.style.width = `${Math.min(pct, 100)}%`; });
  }, [pct]);
  const c = color || (pct > 100 ? "var(--danger)" : pct > 80 ? "var(--warn)" : pct > 30 ? "var(--cyan)" : "var(--ok)");
  return (
    <div className="h-2.5 rounded-full w-full overflow-hidden" style={{ background: "var(--ring-track)" }}>
      <div ref={ref} className="h-full rounded-full" style={{ width: 0, background: c, transition: "width 1s cubic-bezier(.2,.8,.2,1)", boxShadow: `0 0 8px ${c}` }} />
    </div>
  );
}

export const STATUS_COLORS: Record<string, string> = {
  todo: "var(--muted)", in_progress: "var(--cyan)", review: "var(--warn)",
  blocked: "var(--danger)", done: "var(--ok)",
};
export const STATUS_LABELS: Record<string, string> = {
  todo: "To do", in_progress: "In progress", review: "In review",
  blocked: "Blocked", done: "Done",
};
export function StatusChip({ status }: { status: string }) {
  return <span className="chip" style={{ color: STATUS_COLORS[status], borderColor: STATUS_COLORS[status] }}>{STATUS_LABELS[status] || status}</span>;
}
export function PriorityDot({ p }: { p: string }) {
  const c = p === "critical" ? "var(--danger)" : p === "high" ? "var(--warn)" : p === "medium" ? "var(--cyan)" : "var(--muted)";
  return <span title={p} className="inline-block w-2 h-2 rounded-full" style={{ background: c, boxShadow: `0 0 6px ${c}` }} />;
}
