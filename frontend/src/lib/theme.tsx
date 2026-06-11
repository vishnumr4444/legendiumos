"use client";
import { createContext, useContext, useEffect, useState } from "react";

const ThemeCtx = createContext<{ night: boolean; toggle: () => void }>({
  night: true,
  toggle: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [night, setNight] = useState(true);
  useEffect(() => {
    const saved = localStorage.getItem("legendium_theme");
    if (saved) setNight(saved === "night");
  }, []);
  useEffect(() => {
    document.documentElement.classList.toggle("dark", night);
    localStorage.setItem("legendium_theme", night ? "night" : "day");
  }, [night]);
  return (
    <ThemeCtx.Provider value={{ night, toggle: () => setNight((n) => !n) }}>
      {children}
    </ThemeCtx.Provider>
  );
}
export const useTheme = () => useContext(ThemeCtx);
