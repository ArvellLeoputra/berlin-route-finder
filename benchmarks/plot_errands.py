import os

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FixedLocator, FuncFormatter

# Measured on a MacBook Pro (M1 Pro) with benchmarks/benchmark_planner.py, 5 shops per kind
ERRANDS = [1, 2, 3, 4, 5, 6]
TRIPS = [5, 50, 750, 15_000, 375_000, 11_250_000]
SECONDS = [0.06, 0.29, 0.58, 0.84, 1.55, 2.01]


def font(weight, size):
    path = f"fonts/PlusJakartaSans-{weight}.ttf"
    if os.path.exists(path):
        return FontProperties(fname=path, size=size)
    return FontProperties(family="DejaVu Sans", size=size,
                          weight={"Regular": "normal", "Medium": "medium"}.get(weight, "bold"))


def tracked(text):
    return " ".join(text.upper())


def short(v):
    # 1 -> "1×", 1000 -> "1k×", 1000000 -> "1M×"
    for size, unit in [(1e6, "M"), (1e3, "k")]:
        if v >= size:
            return f"{v / size:g}{unit}×"
    return f"{v:g}×"


INK, MUTED, GRID = "#151a24", "#6b7280", "#e5e7eb"
TRIPS_COLOR, TIME_COLOR = "#ef5350", "#0f9d78"

# Growth compared with 1 errand
trips_growth = [t / TRIPS[0] for t in TRIPS]
time_growth = [s / SECONDS[0] for s in SECONDS]

fig, ax = plt.subplots(figsize=(10, 5.6), dpi=160)
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.1, right=0.83, top=0.78, bottom=0.2)

for values, color, name in [(trips_growth, TRIPS_COLOR, "Possible trips"),
                            (time_growth, TIME_COLOR, "Planning time")]:
    ax.plot(ERRANDS, values, color=color, lw=2.4, zorder=3, solid_capstyle="round")
    ax.scatter(ERRANDS, values, s=46, color=color, edgecolor="white", linewidth=2, zorder=4)
    # Direct label at the end of each line: name and final growth
    ax.text(6.18, values[-1], f"{name}\n{short(values[-1])}", va="center",
            fontproperties=font("SemiBold", 11.5), color=INK, linespacing=1.3)

ax.set_yscale("log")
ax.set_ylim(0.5, 1e7)
ax.yaxis.set_major_locator(FixedLocator([1, 10, 100, 1e3, 1e4, 1e5, 1e6]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: short(v)))
ax.minorticks_off()
ax.set_xlim(0.8, 6.15)
ax.set_xticks(ERRANDS)

for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, length=0, pad=6)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(font("Medium", 10.5))
ax.set_xlabel("Errands on the trip", fontproperties=font("Medium", 11), color=MUTED, labelpad=10)

box = ax.get_position()
fig.text(box.x0, 0.925, tracked("Growth compared with 1 errand, log scale"),
         fontproperties=font("SemiBold", 10.5), color=MUTED)
fig.text(box.x0, 0.84, "Trips explode, planning time doesn't",
         fontproperties=font("Bold", 21), color=INK)
fig.text(box.x0, 0.03,
         "6 errands: 11.3 million possible trips, planned in 2.0 s. TU Berlin → Alexanderplatz, "
         "5 shops per kind, MacBook Pro (M1 Pro).",
         fontproperties=font("Regular", 9.5), color=MUTED)

fig.savefig("images/errands-scaling.png", facecolor="white")