'use client'

interface LogoProps {
  size?: number
}

export default function Logo({ size = 36 }: LogoProps) {
  return (
    <div
      className="relative flex items-center justify-center rounded-xl bg-gradient-to-br from-amber-300 via-amber-400 to-orange-600 shadow-glow-sm"
      style={{ width: size, height: size }}
    >
      <span
        className="font-display font-extrabold text-ink-950 leading-none"
        style={{ fontSize: Math.round(size * 0.55) }}
      >
        G
      </span>
      <span
        className="absolute -top-1 -right-1 rounded-full bg-violet-400 ring-2 ring-ink-950"
        style={{ width: Math.max(8, Math.round(size * 0.16)), height: Math.max(8, Math.round(size * 0.16)) }}
      />
    </div>
  )
}
