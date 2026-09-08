'use client'

interface LogoProps {
  size?: number
}

export default function Logo({ size = 36 }: LogoProps) {
  return (
    <div
      className="relative flex items-center justify-center rounded-xl bg-emerald-800 border border-emerald-950/10 shadow-sm"
      style={{ width: size, height: size }}
    >
      <span
        className="font-display font-extrabold text-white leading-none"
        style={{ fontSize: Math.round(size * 0.55) }}
      >
        G
      </span>
      <span
        className="absolute -top-1 -right-1 rounded-full bg-amber-400 ring-2 ring-white"
        style={{ width: Math.max(8, Math.round(size * 0.16)), height: Math.max(8, Math.round(size * 0.16)) }}
      />
    </div>
  )
}
