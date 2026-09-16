const useCases = [
  {
    number: "01",
    title: "Agriculture",
    text: "Explore vegetation and land-cover changes through natural-language analysis.",
  },
  {
    number: "02",
    title: "Disaster Response",
    text: "Support before-and-after assessment workflows for rapidly changing areas.",
  },
  {
    number: "03",
    title: "Urban Planning",
    text: "Investigate built-up growth and spatial changes across time.",
  },
  {
    number: "04",
    title: "Earth Observation",
    text: "Give analysts a simpler interface for interacting with remote-sensing data.",
  },
];

export default function UseCases() {
  return (
    <section
      id="use-cases"
      className="border-y border-border-subtle bg-bg-base py-28"
    >
      <div className="mx-auto max-w-7xl px-5">
        <div className="grid gap-14 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="mb-4 text-xs font-medium uppercase tracking-[0.25em] text-primary">
              Built for Earth intelligence
            </p>

            <h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">
              Turning imagery
              <span className="block text-text-muted">into decisions.</span>
            </h2>

            <p className="mt-6 max-w-md text-sm leading-7 text-text-muted">
              From environmental monitoring to disaster assessment,
              natural-language access can make complex imagery analysis easier
              to explore.
            </p>
          </div>

          <div className="divide-y divide-white/5 rounded-3xl border border-border-subtle bg-white/[0.02]">
            {useCases.map((item) => (
              <div
                key={item.number}
                className="group flex gap-6 p-6 transition hover:bg-white/[0.025] sm:p-8"
              >
                <span className="pt-1 text-xs text-primary">{item.number}</span>

                <div>
                  <h3 className="text-lg font-medium text-text-main transition group-hover:text-primary">
                    {item.title}
                  </h3>

                  <p className="mt-2 max-w-xl text-sm leading-6 text-text-muted">
                    {item.text}
                  </p>
                </div>

                <span className="ml-auto hidden text-slate-700 transition group-hover:text-primary sm:block">
                  ↗
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
