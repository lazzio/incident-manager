/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './templates/**/*.html',
    './incidents/**/*.{py,html}',  // Ajustez selon votre structure
    './static/**/*.js',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: '#99C7FF',  // Bleu pastel
          foreground: '#2E5C99',
        },
        secondary: {
          DEFAULT: '#FFE499',  // Jaune pastel
          foreground: '#99842E',
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: '#F5F5F5',  // Gris très clair
          foreground: '#666666',
        },
        accent: {
          DEFAULT: '#CC99FF',  // Violet pastel
          foreground: '#5C2E99',
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        blue: {
          100: '#E6F3FF',
          500: '#99C7FF',
          800: '#3D7ACC',
          900: '#2E5C99'
        },
        yellow: {
          100: '#FFF8E6',
          500: '#FFE499',
          800: '#CCB13D',
          900: '#99842E'
        },
        green: {
          100: '#E6FFE6',
          500: '#99FF99',
          800: '#3DCC3D',
          900: '#2E992E'
        },
        red: {
          100: '#FFE6E6',
          500: '#FF9999',
          800: '#CC3D3D',
          900: '#992E2E'
        },
        orange: {
          100: '#FFE6CC',
          500: '#FFB366',
          800: '#CC7A1A',
          900: '#995C13'
        },
        purple: {
          100: '#F3E6FF',
          500: '#CC99FF',
          800: '#7A3DCC',
          900: '#5C2E99'
        },
        gray: {
          100: '#F5F5F5',
          500: '#B3B3B3',
          800: '#666666',
          900: '#4D4D4D'
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      fontFamily: {
        sans: ['Quicksand', 'sans-serif'],
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    require("@tailwindcss/forms"),
    require("daisyui") // Ajout du plugin DaisyUI
  ],
  // Configuration de DaisyUI (facultatif)
  daisyui: {
    themes: [
      {
        mytheme: {
          "primary": "#99C7FF",
          "secondary": "#FFE499",
          "accent": "#CC99FF",
          "neutral": "#F5F5F5",
          "base-100": "#ffffff",
          "info": "#3ABFF8",
          "success": "#36D399",
          "warning": "#FBBD23",
          "error": "#F87272",
        },
      },
    ],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    logs: true,
  },
}