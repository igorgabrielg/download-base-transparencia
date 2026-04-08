import type { ReactNode } from "react";

import { ThemeContext, useThemeProvider } from "../hooks/useTheme";

interface Props {
  children: ReactNode;
}

export function ThemeProvider({ children }: Props) {
  const themeCtx = useThemeProvider();

  return (
    <ThemeContext.Provider value={themeCtx}>{children}</ThemeContext.Provider>
  );
}
