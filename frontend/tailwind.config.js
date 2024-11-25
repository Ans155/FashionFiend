/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        shake: 'shake 0.5s',
      },
      keyframes: {
        shake: {
          '0%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-5px)' },
          '50%': { transform: 'translateX(5px)' },
          '75%': { transform: 'translateX(-5px)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
      fontFamily: {
        'sf-pro': ['SF Pro', 'sans-serif'],
      },
      colors: {
        botblue: '#E7ECFC',
        darkbase2: '#1C1C1E',
        lightbase3: '#EBEBEB', 
        darkbase4:'#808080',
        navgray:'#777778',
        lightbase4:'#E1E1E1'
      },
      backgroundImage: {
        'gradient-custom': 'linear-gradient(97.57deg, #ECD996 34.56%, #FFFFFF 49.33%, #ECD996 65.66%)',
      },
    },
  },
  plugins: [],
}
