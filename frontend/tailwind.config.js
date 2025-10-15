/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // More vibrant, visible colors
        primary: "#5b7fd4", // Vibrant blue (was lavender)
        secondary: "#7aa5d1", // Darker powder blue
        accent: "#f5a7c1", // Darker soft pink
        success: "#10b981", // Vibrant emerald green (was pastel)
        danger: "#e89090", // Darker soft coral
        warning: "#f0c875", // Darker moccasin
        background: "#fafafa", // Soft white
        surface: "#ffffff", // Pure white
        textPrimary: "#2d2d2d", // Much darker gray for better readability
        textSecondary: "#5a5a5a", // Darker medium gray
        border: "#e0e0e0", // Slightly darker border
      },
      animation: {
        "spin-slow": "spin 2s linear infinite",
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
