import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: '#FFF8F0',
        orange: {
          warm: '#FF6B35',
        },
        mint: '#4ECDC4',
        dark: '#2D2D2D',
      },
      fontFamily: {
        display: ['Nunito', 'sans-serif'],
        sans: ['DM Sans', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
    },
  },
  plugins: [],
} satisfies Config
