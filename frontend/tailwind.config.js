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
        'gangu': {
          primary: '#1E40AF',    // Professional Blue
          secondary: '#3B82F6',  // Bright Blue
          accent: '#8B5CF6',     // Purple accent
          light: '#F8FAFC',      // Slate white
          dark: '#0F172A',       // Slate 900
          muted: '#64748B',      // Slate 500
          error: '#EF4444',      // Red
          warning: '#F59E0B',    // Amber
          success: '#10B981',    // Emerald
          info: '#06B6D4',       // Cyan
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}
