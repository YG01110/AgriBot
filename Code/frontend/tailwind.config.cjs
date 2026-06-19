module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      maxWidth: {
        '7xl': '80rem'
      },
      colors: {
        sky: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49'
        }
      },
      backdropBlur: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '40px'
      },
      borderColor: {
        DEFAULT: 'rgba(186, 230, 253, 0.3)'
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(14, 165, 233, 0.1)'
      },
      animation: {
        'text-shine': 'text-shine 2s ease-in-out infinite alternate',
        'border-shine': 'border-shine 1.5s linear forwards'
      },
      keyframes: {
        'text-shine': {
          '0%': { 'background-position': '0% 50%' },
          '100%': { 'background-position': '100% 50%' },
        },
        'border-shine': {
          '0%': { 'background-position': '-100% -100%' },
          '100%': { 'background-position': '200% 200%' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}