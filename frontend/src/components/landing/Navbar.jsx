const navItems = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Capabilities", href: "#capabilities" },
  { label: "Use cases", href: "#use-cases" },
];

export default function Navbar({ navigateTo }) {
  return (
    <header className="fixed left-0 right-0 top-0 z-50">
      <div className="mx-auto max-w-7xl px-5 pt-5">
        <nav className="glass flex h-16 items-center justify-between rounded-2xl border border-border-subtle px-5 shadow-2xl shadow-black/20">
          <a href="#" className="flex items-center gap-3">
            <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/30">
              <div className="h-4 w-4 rounded-full border border-primary" />
              <span className="absolute h-1.5 w-1.5 rounded-full bg-primary" />
            </div>

            <div>
              <div className="text-[15px] font-semibold tracking-wide">
                SAT<span className="text-primary">QUERY</span>
              </div>
              <div className="text-[8px] uppercase tracking-[0.3em] text-text-muted">
                Earth Intelligence
              </div>
            </div>
          </a>

          <div className="hidden items-center gap-8 md:flex">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm text-text-muted transition hover:text-text-main"
              >
                {item.label}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={(e) => {
                e.preventDefault();
                if (navigateTo) navigateTo("login");
              }}
              className="text-sm font-medium text-text-main transition hover:text-text-main hidden md:block"
            >
              Sign In
            </button>
            <a
              href="#workspace"
              className="rounded-xl border border-primary/30 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition hover:bg-primary/20"
            >
              Try SatQuery
            </a>
          </div>
        </nav>
      </div>
    </header>
  );
}
