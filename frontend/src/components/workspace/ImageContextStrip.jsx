export default function ImageContextStrip({ images, selectedImage, onSelectImage }) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/10">
      {images.map(img => (
        <div 
          key={img.id}
          onClick={() => onSelectImage(img.id)}
          className={`flex items-center gap-3 p-2 rounded-xl border cursor-pointer min-w-[180px] transition-all ${
            selectedImage === img.id 
              ? "bg-emerald-500/10 border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.1)]" 
              : "bg-surface border-border-subtle hover:border-white/20"
          }`}
        >
          <div className="w-10 h-10 rounded-lg bg-slate-800 overflow-hidden shrink-0">
            <img src={img.url} alt={img.filename} className="w-full h-full object-cover opacity-70" />
          </div>
          <div className="truncate text-xs font-medium text-text-main">
            {img.filename}
          </div>
        </div>
      ))}
    </div>
  );
}
