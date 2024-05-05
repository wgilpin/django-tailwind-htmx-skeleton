/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './doofer/templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
};