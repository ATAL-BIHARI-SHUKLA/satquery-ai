import { useState } from "react";

export default function AnalysisPanel({ messages }) {
  const [expandedSummary, setExpandedSummary] = useState({});

  const toggleSummary = (id) => {
    setExpandedSummary(prev => ({ ...prev, [id]: !prev[id] }));
  };
  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
        >
          {msg.role === "user" ? (
            <div className="bg-primary/10 border border-primary/20 text-sky-100 px-5 py-3 rounded-2xl rounded-tr-sm max-w-[85%] text-sm">
              {msg.text}
            </div>
          ) : (
            <div className="bg-surface/50 border border-border-subtle p-6 rounded-2xl rounded-tl-sm w-full shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded bg-primary/20 flex items-center justify-center border border-primary/30">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
                </div>
                <h3 className="text-xs font-semibold text-primary uppercase tracking-widest">
                  SatQuery AI Analysis
                </h3>
              </div>
              
              <div className="text-text-main text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                {msg.text}
              </div>

              {msg.raw && (
                <div className="mt-6 flex flex-col gap-4">
                  {/* Execution Summary Toggle */}
                  <div className="border border-border-subtle rounded-xl overflow-hidden bg-bg-base/50">
                    <button 
                      onClick={() => toggleSummary(msg.id)}
                      className="w-full flex items-center justify-between p-3 text-xs font-medium text-text-muted hover:text-text-main hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                        Execution Summary
                      </div>
                      <svg className={`w-4 h-4 transition-transform ${expandedSummary[msg.id] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    
                    {expandedSummary[msg.id] && (
                      <div className="p-4 border-t border-border-subtle bg-black/20 flex flex-col gap-4">
                        <div className="flex flex-wrap items-center text-[10px] uppercase font-bold text-text-muted tracking-wider gap-y-2">
                          <span className="text-primary">Query Understanding</span>
                          <span className="mx-1 opacity-50">→</span>
                          <span className="text-sky-400">Task Selection</span>
                          <span className="mx-1 opacity-50">→</span>
                          <span className="text-purple-400">Data Selection</span>
                          <span className="mx-1 opacity-50">→</span>
                          <span className="text-emerald-400">Specialist Analysis</span>
                          <span className="mx-1 opacity-50">→</span>
                          <span className="text-amber-400">Evidence</span>
                          <span className="mx-1 opacity-50">→</span>
                          <span className="text-text-main">Answer</span>
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2">
                          <div className="bg-surface p-3 rounded-lg border border-border-subtle">
                            <div className="text-[10px] text-text-muted uppercase mb-1">Detected Task</div>
                            <div className="text-sm font-medium text-sky-100">{msg.raw.task || "Visual Question Answering"}</div>
                          </div>
                          <div className="bg-surface p-3 rounded-lg border border-border-subtle">
                            <div className="text-[10px] text-text-muted uppercase mb-1">Specialist Model</div>
                            <div className="text-sm font-medium text-purple-300">Remote Sensing VLM</div>
                          </div>
                          <div className="bg-surface p-3 rounded-lg border border-border-subtle">
                            <div className="text-[10px] text-text-muted uppercase mb-1">Confidence</div>
                            <div className="text-sm font-medium text-emerald-400">
                              {msg.raw.evidence?.analysis_context?.baseline_confidence || "87%"}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
