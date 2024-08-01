/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  content: [
    "./src/**/*.{html,js,vue}",
    "./src/*.{html,js,vue}",
    "./src/**/*.vue"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
};