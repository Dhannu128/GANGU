/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12',
        },
        ink: {
          950: '#05070C',
          900: '#0A0E1A',
          850: '#0D1322',
          800: '#121A2E',
          700: '#1A2440',
          600: '#243154',
        },
        gangu: {
          primary: '#FB923C',
          secondary: '#F59E0B',
          accent: '#8B5CF6',
          light: '#F8FAFC',
          dark: '#0A0E1A',
          muted: '#64748B',
          error: '#F43F5E',
          warning: '#F59E0B',
          success: '#10B981',
          info: '#06B6D4',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        display: ['var(--font-jakarta)', '"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      animation: {
        'gradient-x':   'gradient-x 8s ease infinite',
        'shimmer':      'shimmer 2.5s linear infinite',
        'float-slow':   'float 6s ease-in-out infinite',
        'pulse-soft':   'pulse-soft 2.8s ease-in-out infinite',
        'pulse-slow':   'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow':  'bounce 2s infinite',
        'glow':         'glow 3s ease-in-out infinite',
        'rise':         'rise 0.5s ease-out both',
        'spin-slow':    'spin 6s linear infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': { 'background-position': '0% 50%' },
          '50%':      { 'background-position': '100% 50%' },
        },
        shimmer: {
          '0%':   { 'background-position': '-200% 0' },
          '100%': { 'background-position': '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-12px)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.7' },
        },
        glow: {
          '0%, 100%': { 'box-shadow': '0 0 30px -8px rgba(251, 146, 60, 0.5)' },
          '50%':      { 'box-shadow': '0 0 60px -8px rgba(251, 146, 60, 0.85)' },
        },
        rise: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'glow-sm': '0 0 20px -6px rgba(251, 146, 60, 0.45)',
        'glow':    '0 0 40px -8px rgba(251, 146, 60, 0.55)',
        'glow-lg': '0 0 80px -12px rgba(251, 146, 60, 0.6)',
        'card':    '0 30px 80px -30px rgba(0, 0, 0, 0.7)',
      },
    },
  },
  plugins: [],
}
