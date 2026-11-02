import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Theme = "dark" | "light" | "system";
const KEY = "sentinel-ai-theme";
const Ctx = createContext<{ theme: Theme; setTheme: (t: Theme) => void }>({
  theme: "dark",
  setTheme: () => {},
});

function apply(t: Theme) {
  const dark =
    t === "dark" || (t === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.classList.toggle("dark", dark);
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");
  useEffect(() => {
    const saved =
      (localStorage.getItem(KEY) as Theme | null) ??
      (localStorage.getItem("protecto-theme") as Theme | null) ??
      "dark";
    localStorage.setItem(KEY, saved);
    setThemeState(saved);
    apply(saved);
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if ((localStorage.getItem(KEY) ?? "dark") === "system") apply("system");
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  const setTheme = (t: Theme) => {
    localStorage.setItem(KEY, t);
    setThemeState(t);
    apply(t);
  };
  return <Ctx.Provider value={{ theme, setTheme }}>{children}</Ctx.Provider>;
}

export const useTheme = () => useContext(Ctx);
