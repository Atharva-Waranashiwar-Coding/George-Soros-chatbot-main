/** @type {import('tailwindcss').Config} */
import defaultTheme from 'tailwindcss/defaultTheme';

export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'brand-purple': '#6B46C1',
                'brand-purple-light': '#805AD5',
                'brand-purple-dark': '#553C9A',
                'brand-gold': '#D69E2E',
                'brand-gold-light': '#ECC94B',
                'brand-gold-dark': '#B7791F',
                'dark-bg': '#020617',          // slate-950
                'dark-card': '#0F172A',       // slate-900
                'dark-card-hover': '#1E293B', // slate-800
                'dark-input': '#1E293B',      // slate-800
                'dark-text': '#E2E8F0',        // slate-200
                'dark-text-secondary': '#94A3B8', // slate-400
                'dark-border': '#1E293B',      // slate-800
                'tooltip-bg': '#1E293B',      // slate-800
                'message-area-bg': 'rgba(0, 0, 0, 0.4)',
            },
            fontFamily: {
                sans: ['Inter', ...defaultTheme.fontFamily.sans], // Inter remains default sans
                serif: ['Playfair Display', ...defaultTheme.fontFamily.serif], // Added Playfair Display
            },
        },
    },
    plugins: [
        // require('@tailwindcss/forms'),
    ],
}
