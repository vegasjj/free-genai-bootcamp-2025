/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0d6efd',
          hover: '#0b5ed7',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#6c757d',
          foreground: '#ffffff',
        },
      },
    },
  },
  plugins: [],
}
