import React from "react";

export default function WorkspaceNavbar({
  selectedConversation,
  setIsMobileSidebarOpen,
  navigateTo,
}) {
  return (
    <header className="h-14 shrink-0 flex items-center justify-between px-4 border-b border-border-subtle bg-surface/50 backdrop-blur-sm z-10">
      <div className="flex items-center gap-3">
        <button
          className="md:hidden p-2 -ml-2 text-text-muted hover:text-text-main rounded-lg hover:bg-white/5"
          onClick={() => setIsMobileSidebarOpen(true)}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-primary/10 border border-primary/20">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
          <span className="text-[10px] uppercase font-bold text-primary tracking-widest">
            SatQuery AI
          </span>
        </div>
        {/* Back Button */}
        <button
          className="ml-2 px-3 py-1.5 rounded-md text-xs font-medium text-text-muted hover:text-text-main hover:bg-white/5 transition-colors border border-border-subtle"
          onClick={() => navigateTo("home")}
        >
          Exit
        </button>
      </div>
    </header>
  );
}
