export default function CTA() {
  return (
    <section className="relative overflow-hidden py-28">
      <div className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]" />

      <div className="relative mx-auto max-w-5xl px-5">
        <div className="overflow-hidden rounded-[2rem] border border-primary/15 bg-gradient-to-br from-primary/[0.08] to-secondary/[0.03] p-10 text-center sm:p-16">
          <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 text-primary">
            ✦
          </div>

          <h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">
            Don't learn how to analyse
            <span className="block text-primary">satellite data. Ask it.</span>
          </h2>

          <p className="mx-auto mt-5 max-w-xl text-sm leading-6 text-text-muted">
            Upload an image, ask a question and let SatQuery turn your
            natural-language intent into a remote-sensing workflow.
          </p>

          <a
            href="#workspace"
            className="mt-8 inline-flex rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-primary"
          >
            Try SatQuery AI →
          </a>
        </div>
      </div>
    </section>
  );
}
