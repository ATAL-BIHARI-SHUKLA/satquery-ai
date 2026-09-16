export default function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-base">
      <div className="mx-auto max-w-7xl px-5 py-10">
        <div className="flex flex-col justify-between gap-8 sm:flex-row sm:items-center">
          <div>
            <div className="text-sm font-semibold tracking-wide">
              SAT<span className="text-primary">QUERY</span>
            </div>

            <p className="mt-2 text-xs text-text-muted">
              Interactive vision-language intelligence for satellite imagery.
            </p>
          </div>

          <div className="flex gap-6 text-xs text-text-muted">
            <a href="#how-it-works" className="hover:text-text-main">
              How it works
            </a>

            <a href="#capabilities" className="hover:text-text-main">
              Capabilities
            </a>

            <a href="#use-cases" className="hover:text-text-main">
              Use cases
            </a>
          </div>
        </div>

        <div className="mt-8 border-t border-border-subtle pt-6 text-[10px] text-slate-700">
          © 2026 SatQuery AI · Satellite Intelligence Interface
        </div>
      </div>
    </footer>
  );
}
