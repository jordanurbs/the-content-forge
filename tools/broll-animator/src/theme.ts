import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";

export interface ThemeColors {
  primary: string;
  accent: string;
  secondary: string;
}

export interface Theme {
  colors: ThemeColors;
  fonts?: {
    heading?: string;
    body?: string;
    mono?: string;
  };
  brandLogo?: string;
  brandName?: string;
}

const DEFAULT_THEME: Theme = {
  colors: {
    primary: "#0a0e1a",
    accent: "#FFD700",
    secondary: "#00FFFF",
  },
  fonts: {
    heading: "system-ui, -apple-system, sans-serif",
    body: "system-ui, -apple-system, sans-serif",
    mono: "ui-monospace, Menlo, monospace",
  },
  brandLogo: "",
  brandName: "",
};

function findThemePath(): string | null {
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    const candidate = join(dir, "config", "theme.json");
    if (existsSync(candidate)) return candidate;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

export function loadTheme(): Theme {
  const path = findThemePath();
  if (!path) return DEFAULT_THEME;
  try {
    const raw = readFileSync(path, "utf8");
    const parsed = JSON.parse(raw) as Partial<Theme>;
    return {
      colors: { ...DEFAULT_THEME.colors, ...(parsed.colors || {}) },
      fonts: { ...DEFAULT_THEME.fonts, ...(parsed.fonts || {}) },
      brandLogo: parsed.brandLogo ?? DEFAULT_THEME.brandLogo,
      brandName: parsed.brandName ?? DEFAULT_THEME.brandName,
    };
  } catch {
    return DEFAULT_THEME;
  }
}

const theme = loadTheme();
export const PRIMARY = theme.colors.primary;
export const ACCENT = theme.colors.accent;
export const SECONDARY = theme.colors.secondary;

// Legacy aliases for existing card components
export const NAVY = PRIMARY;
export const GOLD = ACCENT;
export const CYAN = SECONDARY;
