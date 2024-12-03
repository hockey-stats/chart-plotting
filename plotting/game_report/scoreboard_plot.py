import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from plotting.plot import Plot, get_logo_marker

plot = Plot(filename='test.png')
fig, ax = plot.fig, plot.axis

ax.text(0.5, 0.75, "Goals",
        size=25,
        ha='center',
        va='center',
        bbox={
            "boxstyle": "round",
            })

ax.text(0.35, 0.75, "4",
        size=25,
        ha='center',
        va='center')

ax.text(0.65, 0.75, "0",
        size=25,
        ha='center',
        va='center')

ax.text(0.5, 0.65, "xGoals",
        size=25,
        ha='center',
        va='center',
        bbox={
            "boxstyle": "round",
            })

ax.text(0.35, 0.65, "5.4",
        size=25,
        ha='center',
        va='center')

ax.text(0.65, 0.65, "2.5",
        size=25,
        ha='center',
        va='center')


logo_a = AnnotationBbox(get_logo_marker(('TOR'), alpha=0.8, zoom=2),
                      xy=(0.2, 0.9), frameon=False)
logo_b = AnnotationBbox(get_logo_marker(('MTL'), alpha=0.8, zoom=2),
                      xy=(0.8, 0.9), frameon=False)

ax.add_artist(logo_a)
ax.add_artist(logo_b)

plot.save_plot()