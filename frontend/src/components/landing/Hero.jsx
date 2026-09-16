import heroImg from '../../assets/hero.png';

export default function Hero({ navigateTo }) {
  return (
    <section className="relative overflow-hidden bg-[#07111F] pt-32 pb-16 lg:pb-32">
      {/* Subtle atmospheric glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-secondary/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-primary/10 blur-[150px]" />
      </div>

      {/* Decorative stars */}
      <div className="absolute left-[10%] top-[25%] h-1 w-1 rounded-full bg-[#22D3A6]/80" />
      <div className="absolute right-[14%] top-[32%] h-1 w-1 rounded-full bg-white/70" />
      <div className="absolute left-[18%] top-[70%] h-1 w-1 rounded-full bg-white/40" />
      <div className="absolute right-[22%] top-[65%] h-1.5 w-1.5 rounded-full bg-[#4DA3FF]/60" />

      <div className="relative mx-auto max-w-7xl px-5">
        {/* Two-Column Hero Content */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Column: Text & CTA */}
          <div className="flex flex-col items-start text-left">
            <h1 className="text-5xl font-bold leading-[1.1] tracking-tight sm:text-6xl md:text-7xl text-text-main">
              Don't just see the Earth.<br />
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Understand it.
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-lg text-text-muted leading-relaxed">
              Upload an image, ask a question and let SatQuery turn your natural-language intent into powerful remote-sensing analysis.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
              <button
                onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                className="w-full sm:w-auto rounded-xl bg-[#22D3A6] px-8 py-4 text-sm font-semibold text-slate-900 transition hover:opacity-90 flex justify-center items-center gap-2"
              >
                Try SatQuery AI &rarr;
              </button>
              <button className="w-full sm:w-auto rounded-xl bg-black/20 border border-border-subtle px-8 py-4 text-sm font-semibold text-[#4DA3FF] transition hover:bg-white/5 flex justify-center items-center">
                See how it works
              </button>
            </div>

            {/* Trust/Features */}
            <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-text-muted font-medium">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-[#22D3A6]"></span>
                Multimodal (Optical + SAR)
              </div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-[#22D3A6]"></span>
                Natural language
              </div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-[#22D3A6]"></span>
                Evidence-based results
              </div>
            </div>
          </div>

          {/* Right Column: Visual Area */}
          <div className="relative mt-16 lg:mt-0 w-full flex justify-center lg:justify-end">
            <div className="absolute inset-0 bg-[#4DA3FF]/10 blur-[100px] rounded-full pointer-events-none" />
            
            <div className="relative w-full max-w-md lg:max-w-lg aspect-square rounded-full border border-border-subtle/30 bg-[#0D1B2A]/50 backdrop-blur-sm flex items-center justify-center p-8">
              {/* Orbit lines */}
              <div className="absolute inset-4 rounded-full border border-dashed border-border-subtle/30 animate-[spin_60s_linear_infinite]" />
              <div className="absolute inset-12 rounded-full border border-dashed border-border-subtle/40 animate-[spin_40s_linear_infinite_reverse]" />
              
              {/* Earth Asset */}
              <div className="relative w-3/4 h-3/4 rounded-full overflow-hidden border border-[#22D3A6]/20 shadow-[0_0_50px_rgba(34,211,166,0.15)] bg-[#07111F]">
                <img src={heroImg} alt="Earth Observation" className="w-full h-full object-cover opacity-80" />
              </div>

              {/* Floating Info Card */}
              <div className="absolute -bottom-4 -left-4 sm:bottom-0 sm:-left-8 z-10 p-5 rounded-2xl border border-border-subtle bg-surface/90 backdrop-blur-md shadow-2xl max-w-[260px]">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-2 h-2 rounded-full bg-[#22D3A6] animate-pulse" />
                  <span className="text-[10px] uppercase tracking-wider text-[#22D3A6] font-semibold">Live Analysis</span>
                </div>
                <p className="text-sm font-medium text-text-main mb-3">Turning satellite data into real-world impact.</p>
                <div className="flex flex-wrap gap-2 text-[10px] text-text-muted">
                  <span className="px-2 py-1 rounded bg-black/30 border border-white/5">Accessible</span>
                  <span className="px-2 py-1 rounded bg-black/30 border border-white/5">Accurate</span>
                  <span className="px-2 py-1 rounded bg-black/30 border border-white/5">Actionable</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
