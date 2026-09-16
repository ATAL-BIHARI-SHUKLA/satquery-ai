export default function ConversationSidebar({ conversations, selectedConversation, onSelectConversation, onNewConversation, navigateTo }) {
  return (
    <div className="flex flex-col h-full bg-surface/30">
      <div className="p-5 flex items-center justify-between border-b border-border-subtle">
        <h2 className="font-bold text-text-main text-lg tracking-tight flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-primary/20 border border-primary/30 flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-primary"></div>
          </div>
          SatQuery
        </h2>
        <button onClick={() => navigateTo("home")} className="md:hidden text-text-muted hover:text-text-main transition p-1">
          ✕
        </button>
      </div>

      <div className="p-4">
        <button 
          onClick={onNewConversation}
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-primary text-slate-900 hover:bg-primary/90 transition text-sm font-semibold shadow-[0_0_15px_rgba(34,211,166,0.2)]"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Analysis
        </button>
      </div>

      <div className="flex flex-col gap-1 flex-1 overflow-y-auto px-2 pb-4 scrollbar-thin scrollbar-thumb-white/5">
        
        {/* Saved Analyses (Placeholder for future) */}
        <div className="mt-2 mb-4 px-2">
          <div className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-2 flex items-center gap-2">
            Saved Analyses
            <span className="text-[8px] bg-white/10 px-1.5 py-0.5 rounded text-white/40">BETA</span>
          </div>
          <button className="text-left w-full p-2 rounded-lg text-sm text-text-muted hover:bg-white/5 transition-colors flex items-center gap-2 opacity-50 cursor-not-allowed" disabled>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            No saved templates
          </button>
        </div>

        <div className="px-2 text-[10px] font-bold text-text-muted uppercase tracking-widest mb-2 mt-2">
          Recent History
        </div>
        
        {conversations.length === 0 ? (
          <div className="px-4 py-3 text-xs text-text-muted text-center italic">No recent history</div>
        ) : (
          conversations.map(conv => (
            <button 
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`text-left px-3 py-2.5 rounded-lg text-sm transition-all border ${
                selectedConversation === conv.id 
                  ? "bg-primary/10 border-primary/20 text-sky-100 font-medium" 
                  : "bg-transparent border-transparent text-text-muted hover:bg-white/5 hover:text-text-main"
              }`}
            >
              <div className="truncate flex items-center gap-2">
                <svg className="w-4 h-4 shrink-0 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                {conv.title}
              </div>
            </button>
          ))
        )}
      </div>

      <div className="p-4 border-t border-border-subtle mt-auto bg-surface/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-purple-500/20">
              U
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-text-main">Analyst</span>
              <span className="text-[10px] text-text-muted">Pro Tier</span>
            </div>
          </div>
          <button 
            onClick={() => {
              localStorage.removeItem("token");
              navigateTo("login");
            }}
            className="p-2 text-text-muted hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
            title="Logout"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
