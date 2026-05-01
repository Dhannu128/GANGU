'use client'

const STACK = [
  { name: 'Google Gemini', sub: 'AI reasoning' },
  { name: 'LangGraph',     sub: 'agent orchestration' },
  { name: 'OpenAI Whisper',sub: 'voice transcription' },
  { name: 'MongoDB',       sub: 'state & memory' },
  { name: 'MCP Protocol',  sub: 'platform integrations' },
]

export default function BuiltWithBar() {
  return (
    <section className="relative max-w-7xl mx-auto px-6 py-12">
      <p className="text-center text-[11px] text-slate-500 uppercase tracking-[0.25em] font-bold mb-6">
        Powered by best-in-class AI infrastructure
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {STACK.map((tech, i) => (
          <div
            key={i}
            className="surface-card px-4 py-4 flex flex-col items-center text-center hover:-translate-y-0.5 transition-transform"
          >
            <span className="font-display font-bold text-sm md:text-[15px] text-slate-200 leading-tight">
              {tech.name}
            </span>
            <span className="text-[10px] uppercase tracking-[0.18em] font-semibold text-slate-500 mt-1.5">
              {tech.sub}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
