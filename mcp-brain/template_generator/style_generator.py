"""
Style Generator — Phase 3 Module
Converts style instructions from the parsed spec into a
Tailwind CSS configuration and a base stylesheet.
"""

import json
import os
import logging
import textwrap

logger = logging.getLogger(__name__)


# ── Tailwind class map per theme ────────────────────────────────────
GLASSMORPHIC_DARK_CLASSES = {
    "container": "bg-black/40 backdrop-blur-lg border border-white/10 rounded-xl",
    "card": "bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl",
    "button_primary": "bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-lg shadow-indigo-500/25",
    "button_secondary": "bg-white/10 hover:bg-white/20 text-white border border-white/10 rounded-xl",
    "heading": "text-white font-extrabold",
    "subtext": "text-gray-400",
    "input": "bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-indigo-500",
    "badge": "bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 rounded-full px-3 py-1 text-sm",
}

GLASSMORPHIC_LIGHT_CLASSES = {
    "container": "bg-white/60 backdrop-blur-lg border border-gray-200 rounded-xl",
    "card": "bg-white/80 backdrop-blur-md border border-gray-200 rounded-2xl",
    "button_primary": "bg-blue-600 hover:bg-blue-500 text-white rounded-xl shadow-lg shadow-blue-500/25",
    "button_secondary": "bg-gray-100 hover:bg-gray-200 text-gray-900 border border-gray-300 rounded-xl",
    "heading": "text-gray-900 font-extrabold",
    "subtext": "text-gray-600",
    "input": "bg-white border border-gray-300 text-gray-900 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500",
    "badge": "bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-3 py-1 text-sm",
}


class StyleGenerator:
    """Generate Tailwind configuration and base CSS from a template spec."""

    async def generate(self, spec: dict, output_dir: str) -> dict:
        """
        Parameters
        ----------
        spec : dict       — parsed template specification
        output_dir : str  — project root

        Returns
        -------
        dict — summary of generated style artifacts
        """
        style = spec.get("style", {})
        theme = style.get("theme", "dark")
        accent = style.get("accent_color", "#6366f1")
        surface = style.get("surface_color", "#0f172a")

        # 1. tailwind.config.js
        tw_config = self._build_tailwind_config(theme, accent, surface)
        tw_path = os.path.join(output_dir, "tailwind.config.js")
        with open(tw_path, "w") as f:
            f.write(tw_config)
        logger.info("tailwind.config.js → %s", tw_path)

        # 2. postcss.config.js
        postcss_path = os.path.join(output_dir, "postcss.config.js")
        with open(postcss_path, "w") as f:
            f.write(self._postcss_config())

        # 3. Base stylesheet  (src/styles/tailwind.css)
        styles_dir = os.path.join(output_dir, "src", "styles")
        os.makedirs(styles_dir, exist_ok=True)
        css_path = os.path.join(styles_dir, "tailwind.css")
        with open(css_path, "w") as f:
            f.write(self._base_css(theme, accent, surface))
        logger.info("tailwind.css → %s", css_path)

        # 4. Resolve utility class map
        class_map = GLASSMORPHIC_DARK_CLASSES if theme == "dark" else GLASSMORPHIC_LIGHT_CLASSES
        class_map_path = os.path.join(styles_dir, "class_map.json")
        with open(class_map_path, "w") as f:
            json.dump(class_map, f, indent=2)

        return {
            "tailwind_config": tw_path,
            "stylesheet": css_path,
            "class_map": class_map,
            "theme": theme,
        }

    # ── Tailwind config builder ─────────────────────────────────────
    def _build_tailwind_config(self, theme: str, accent: str, surface: str) -> str:
        return textwrap.dedent(f"""\
            /** @type {{import('tailwindcss').Config}} */
            export default {{
              content: [
                './index.html',
                './src/**/*.{{js,jsx,ts,tsx}}',
              ],
              theme: {{
                extend: {{
                  colors: {{
                    accent: '{accent}',
                    surface: '{surface}',
                  }},
                  fontFamily: {{
                    sans: ['Inter', 'system-ui', 'sans-serif'],
                  }},
                  backdropBlur: {{
                    xs: '2px',
                  }},
                  animation: {{
                    'fade-in': 'fadeIn 0.6s ease-out forwards',
                    'slide-up': 'slideUp 0.6s ease-out forwards',
                  }},
                  keyframes: {{
                    fadeIn: {{
                      from: {{ opacity: '0' }},
                      to: {{ opacity: '1' }},
                    }},
                    slideUp: {{
                      from: {{ opacity: '0', transform: 'translateY(20px)' }},
                      to: {{ opacity: '1', transform: 'translateY(0)' }},
                    }},
                  }},
                }},
              }},
              plugins: [],
            }};
        """)

    def _postcss_config(self) -> str:
        return textwrap.dedent("""\
            export default {
              plugins: {
                tailwindcss: {},
                autoprefixer: {},
              },
            };
        """)

    def _base_css(self, theme: str, accent: str, surface: str) -> str:
        bg = surface if theme == "dark" else "#ffffff"
        text = "#f8fafc" if theme == "dark" else "#0f172a"
        return textwrap.dedent(f"""\
            @tailwind base;
            @tailwind components;
            @tailwind utilities;

            @layer base {{
              :root {{
                --color-accent: {accent};
                --color-surface: {surface};
              }}

              body {{
                @apply antialiased;
                background-color: {bg};
                color: {text};
                font-family: 'Inter', system-ui, sans-serif;
              }}

              * {{
                scrollbar-width: thin;
                scrollbar-color: rgba(255,255,255,0.1) transparent;
              }}
            }}

            @layer components {{
              .glass-card {{
                @apply bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl;
              }}

              .glass-card-light {{
                @apply bg-white/60 backdrop-blur-lg border border-gray-200 rounded-2xl;
              }}

              .gradient-accent {{
                background: linear-gradient(135deg, {accent}, color-mix(in srgb, {accent} 60%, #ec4899));
              }}
            }}
        """)
