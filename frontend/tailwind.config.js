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
          50:  '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          300: '#5EEAD4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
          800: '#115E59',
          900: '#134E4A',
        },
        ink: {
          950: '#061521',
          900: '#102033',
          850: '#17263A',
          800: '#213247',
          700: '#30445B',
          600: '#4F6072',
        },
        gangu: {
          primary: '#0F766E',
          secondary: '#B45309',
          accent: '#4F46A5',
          light: '#F3F7FB',
          dark: '#102033',
          muted: '#4F6072',
          error: '#B42318',
          warning: '#B45309',
          success: '#0F766E',
          info: '#0E7490',
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
          '0%, 100%': { 'box-shadow': '0 0 30px -8px rgba(15, 118, 110, 0.42)' },
          '50%':      { 'box-shadow': '0 0 60px -8px rgba(15, 118, 110, 0.70)' },
        },
        rise: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'glow-sm': '0 0 20px -6px rgba(15, 118, 110, 0.40)',
        'glow':    '0 0 40px -8px rgba(15, 118, 110, 0.50)',
        'glow-lg': '0 0 80px -12px rgba(15, 118, 110, 0.56)',
        'card':    '0 24px 70px -36px rgba(16, 32, 51, 0.28)',
      },
    },
  },
  plugins: [],
}
