import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Menu } from "lucide-react";

import { Sidebar } from "./Sidebar";

export function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 lg:ml-60 min-w-0 transition-[margin] duration-200">
        <header className="lg:hidden sticky top-0 z-30 flex items-center gap-3 px-4 h-14 border-b" style={{ backgroundColor: "var(--theme-surface-1)", borderColor: "var(--theme-border)" }}>
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md hover:bg-[var(--theme-surface-2)] transition-colors"
            aria-label="Abrir menu"
          >
            <Menu size={20} style={{ color: "var(--theme-text)" }} />
          </button>
          <span className="text-h5 text-[var(--theme-text)]">Base Transparencia</span>
        </header>

        <main className="p-6 lg:p-8" style={{ backgroundColor: "var(--theme-bg-secondary)", color: "var(--theme-text)", minHeight: "100vh" }}>
          <div className="max-w-[1200px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
