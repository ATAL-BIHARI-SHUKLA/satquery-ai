import { useRef } from "react";

export default function ConversationInput({ currentQuery, setCurrentQuery, onSubmit, loading, onFileUpload, uploading, isLarge = false }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      if (onFileUpload) {
        onFileUpload(e.target.files[0]);
      }
      e.target.value = null;
    }
  };

  return (
    <div className={`bg-surface border border-border-subtle rounded-2xl flex items-end gap-2 shadow-xl shadow-black/50 transition-all ${isLarge ? "p-3 sm:p-4" : "p-2"}`}>
      <input 
        type="file" 
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*"
        className="hidden"
      />
      <button 
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading || loading}
        className={`text-text-muted hover:text-primary transition-colors bg-white/5 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shrink-0 ${isLarge ? "p-4" : "p-3"}`}
      >
        {uploading ? (
          <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
             <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
             <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        )}
      </button>
      
      <textarea 
        value={currentQuery}
        onChange={(e) => setCurrentQuery(e.target.value)}
        onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (currentQuery.trim() && !loading && onSubmit) {
                    onSubmit();
                }
            }
        }}
        className={`flex-1 bg-transparent border-none outline-none resize-none text-text-main placeholder:text-text-muted max-h-32 px-2 ${isLarge ? "text-base py-4" : "text-sm py-3"}`}
        rows={1}
        disabled={loading}
      />
      
      <button 
        onClick={onSubmit}
        disabled={!currentQuery.trim() || loading}
        className={`bg-primary text-slate-950 font-semibold rounded-xl transition-all hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0 ${isLarge ? "px-6 py-4 text-base" : "px-5 py-3 text-sm"}`}
      >
        {loading ? "Analyzing..." : "Ask"}
      </button>
    </div>
  );
}
