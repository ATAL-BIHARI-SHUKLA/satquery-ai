const steps = [
  {
    number: "01",
    title: "Upload imagery",
    description:
      "Add a satellite image or supported multi-image observation to begin your analysis.",
  },
  {
    number: "02",
    title: "Ask naturally",
    description:
      "Describe what you want to know using ordinary language instead of selecting complex tools.",
  },
  {
    number: "03",
    title: "AI routes the task",
    description:
      "SatQuery identifies the analysis task and selects the appropriate specialist workflow.",
  },
  {
    number: "04",
    title: "Get evidence",
    description:
      "Receive an answer together with visual evidence, confidence information and analysis context.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="border-t border-border-subtle bg-bg-base py-28"
    >
      <div className="mx-auto max-w-7xl px-5">
        <div className="max-w-2xl">
          <p className="mb-4 text-xs font-medium uppercase tracking-[0.25em] text-primary">
            How it works
          </p>

          <h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">
            From question to
            <span className="text-text-muted"> satellite intelligence.</span>
          </h2>
        </div>

        <div className="mt-16 grid gap-px overflow-hidden rounded-3xl border border-border-subtle bg-white/8 md:grid-cols-4">
          {steps.map((step) => (
            <div
              key={step.number}
              className="bg-surface p-7 transition hover:bg-surface sm:p-8"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-primary">{step.number}</span>

                <div className="h-px w-12 bg-slate-800" />
              </div>

              <h3 className="mt-14 text-lg font-medium text-text-main">
                {step.title}
              </h3>

              <p className="mt-3 text-sm leading-6 text-text-muted">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
