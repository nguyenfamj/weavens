/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        montserrat: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@assistant-ui/react/tailwindcss')({
      components: ['thread'],
    }),
    require('@assistant-ui/react-markdown/tailwindcss'),
  ],
};
