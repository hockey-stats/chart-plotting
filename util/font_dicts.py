"""
Module to store dicts used for different font sets that may be used in multiple places
"""

import matplotlib.patheffects as PathEffects


label_text_params = {
    "color": "antiquewhite",
    "fontsize": 15,
    "family": "sans-serif",
    "fontweight": 800,
    "path_effects": [PathEffects.withStroke(linewidth=1.5, foreground='maroon')]
}

title_params = {
    "color": "antiquewhite",
    "fontsize": 20,
    "family": "sans-serif",
    "fontweight": 800,
    "path_effects": [PathEffects.withStroke(linewidth=2, foreground='maroon')]
}

subtitle_params = {
    "color": "antiquewhite",
    "size": 13,
    "family": "sans-serif",
    "fontweight": 700,
    #"path_effects": [PathEffects.withStroke(linewidth=2.5, foreground='maroon')]
}

multiplot_title_params = {
    "color": "antiquewhite",
    "size": 35.0,
    "family": "sans-serif",
    "weight": 800,
    "path_effects": [PathEffects.withStroke(linewidth=2.5, foreground='maroon')]
}

multiplot_subtitle_params = {
    "color": "antiquewhite",
    "size": 25.0,
    "family": "sans-serif",
    "weight": 700,
    "path_effects": [PathEffects.withStroke(linewidth=2.5, foreground='maroon')]
}

game_report_label_text_params = {
    "color": "antiquewhite",
    "fontsize": 15,
    "family": "sans-serif",
    "fontweight": 800,
    "path_effects": [PathEffects.withStroke(linewidth=1.2, foreground='black')]
}
