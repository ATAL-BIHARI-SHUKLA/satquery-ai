const capabilities = [
  {
    code: "VQA",
    title: "Visual Question Answering",
    description:
      "Ask questions about objects, land cover and visual content in satellite imagery.",
    icon: "◉",
  },
  {
    code: "CD",
    title: "Change Detection",
    description:
      "Compare imagery from different points in time and identify meaningful changes.",
    icon: "◌",
  },
  {
    code: "SAR",
    title: "Optical + SAR",
    description:
      "Bring complementary optical and radar observations into a multimodal workflow.",
    icon: "⌁",
  },
  {
    code: "GND",
    title: "Visual Grounding",
    description:
      "Connect answers to specific regions or objects within the analyzed imagery.",
    icon: "⊙",
  },
];

export default function Capabilities() {
  return (
    <section id="capabilities" className="relative overflow-hidden py-28">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_50%,rgba(14,165,233,0.07),transparent_30%)]" />

      <div className="relative mx-auto max-w-7xl px-5">
        <div className="flex flex-col justify-between gap-8 md:flex-row md:items-end">
          <div>
            <p className="mb-4 text-xs font-medium uppercase tracking-[0.25em] text-primary">
              Capabilities
            </p>

            <h2 className="max-w-3xl text-3xl font-semibold tracking-tight sm:text-5xl">
              One interface.
              <br />
              <span className="text-text-muted">
                Multiple remote-sensing workflows.
              </span>
            </h2>
          </div>

          <p className="max-w-sm text-sm leading-6 text-text-muted">
            SatQuery is designed around task-specific analysis rather than
            treating every satellite question as a generic chatbot request.
          </p>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-2">
          {capabilities.map((item, index) => (
            <div
              key={item.code}
              className="group relative overflow-hidden rounded-3xl border border-border-subtle bg-white/[0.025] p-7 transition duration-300 hover:-translate-y-1 hover:border-primary/20 hover:bg-primary/[0.025] sm:p-9"
            >
              <div className="absolute right-0 top-0 h-32 w-32 rounded-full bg-primary/5 blur-3xl transition group-hover:bg-primary/10" />

              <div className="relative flex items-start justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-border-subtle bg-white/[0.03] text-xl text-primary">
                  {item.icon}
                </div>

                <span className="text-[10px] tracking-[0.25em] text-text-muted">
                  {item.code}
                </span>
              </div>

              <div className="relative mt-12">
                <span className="text-xs text-primary">0{index + 1}</span>

                <h3 className="mt-2 text-xl font-medium">{item.title}</h3>

                <p className="mt-3 max-w-md text-sm leading-6 text-text-muted">
                  {item.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
