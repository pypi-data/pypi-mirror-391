#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import matplotlib.pyplot as plt
import numpy as np

def hill_plot(
    *args,
    labels=None,
    ylabel=None,
    xlabel=None,
    xlim=None,
    title=None,
    widths=0.7,
    bw_method=0.3,
    jitter_amount=0.1,
    side="upper",
    show_stats=True,
    ax=None,
):
    """
    Experimental
    """
    plt.style.use("default")
    plt.rcParams["font.family"] = "DejaVu Sans"

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, len(args) * 1.5))
        created_fig = True

    n = len(args)

    # --- Clean and filter data ---
    cleaned_args = []
    valid_labels = []
    for i, (arr, lbl) in enumerate(zip(args, labels or [])):
        arr = np.array(arr, dtype=float)
        arr = arr[np.isfinite(arr)]  # Remove NaN and inf
        if len(arr) == 0:
            print(f"⚠️ Skipping '{lbl}' — empty after cleaning.")
            continue
        if np.all(arr == arr[0]):  # All same values
            arr = np.append(arr, arr[0] + 1e-6)  # Add a small epsilon to avoid KDE error
        cleaned_args.append(arr)
        valid_labels.append(lbl if labels is not None else f"Group {i+1}")

    if len(cleaned_args) == 0:
        raise ValueError("All input groups are empty — nothing to plot.")

    args = cleaned_args
    labels = valid_labels
    n = len(args)

    colors = plt.cm.tab10.colors
    if len(colors) < n:
        colors = [colors[i % len(colors)] for i in range(n)]

    # --- Violin plot ---
    parts = ax.violinplot(
        args,
        vert=False,
        showmeans=False,
        showmedians=False,
        widths=widths,
        bw_method=bw_method,
    )

    # Remove the default bars
    for key in ["cbars", "cmins", "cmaxes", "cmedians"]:
        if key in parts:
            parts[key].set_visible(False)

    # --- Style violins ---
    for i, pc in enumerate(parts["bodies"]):
        verts = pc.get_paths()[0].vertices
        y_center = i + 1
        if side == "upper":
            verts[:, 1] = np.maximum(verts[:, 1], y_center)
        else:
            verts[:, 1] = np.minimum(verts[:, 1], y_center)
        pc.set_facecolor(colors[i])
        pc.set_edgecolor(colors[i])
        pc.set_linewidth(1.5)
        pc.set_alpha(0.3)

    # --- Strip points ---
    for i, x in enumerate(args, start=1):
        jitter = (np.random.rand(len(x)) - 0.5) * jitter_amount
        y_positions = np.full(len(x), i) + jitter
        ax.scatter(
            x,
            y_positions,
            color=colors[i - 1],
            alpha=0.6,
            s=25,
            edgecolor="white",
            linewidth=0.8,
            zorder=2,
        )

    # --- Stats ---
    if show_stats:
        for i, (pc, x) in enumerate(zip(parts["bodies"], args), start=1):
            x = np.array(x)
            mean_val, median_val, std_val = np.mean(x), np.median(x), np.std(x)
            verts = pc.get_paths()[0].vertices

            triangle_offset = 0.05
            mean_y = i + (widths / 2 if side == "upper" else -widths / 2)
            median_y = i - (widths / 2 if side == "upper" else +widths / 2)

            ax.scatter(mean_val, mean_y, marker="^", s=30,
                       facecolor=colors[i - 1], edgecolor="black", linewidth=0.5, zorder=6)
            ax.text(mean_val, mean_y - 0.07, f"mean: {mean_val:.2f} ± {std_val:.2f}",
                    ha="center", va="top", fontsize=8)

            ax.scatter(median_val, median_y, marker="v", s=30,
                       facecolor=colors[i - 1], edgecolor="black", linewidth=0.5, zorder=6)
            ax.text(median_val, median_y + 0.07, f"median: {median_val:.2f}",
                    ha="center", va="bottom", fontsize=8)

    # --- Axis setup ---
    ax.set_yticks(range(1, n + 1))
    ax.set_yticklabels(labels, fontsize=9)
    ax.tick_params(axis="x", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--", linewidth=0.5)

    if xlim is not None:
        ax.set_xlim(xlim)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if title:
        ax.set_title(title, fontsize=10, pad=20)

    plt.tight_layout()
    plt.close()
    return fig if created_fig else ax


#def plot(*args, ylim=None, xlim=None, label=None, ylabel=None, xlabel=None):
#   """
#   To create 1D/2D plot for immediate
#   inspection.
#
#   Parameters
#   ----------
#   *args: ndarray
#       Arrays to be plotted.
#   ylim: tuple
#       y-lim for the plot.
#       Default: None
#   xlim: tuple
#       x-lim for the plot.
#       Default: None
#   label: str
#       Label for the plot.
#       Legend will use this.
#       Default: None
#   ylabel: str
#       y-label for the plot.
#       Default: None
#   xlabel: str
#       x-label for the plot.
#       Default: None
#   
#   Returns
#   -------
#   Canvas
#       A canvas object with painted data.
#   """
#   n = len(args)
#   
#   if n < 1:
#       raise ValueError("Need minimum 1 positional argument")
#       
#       ## 1D Array
#   if args[0].ndim == 1:
#       cv = CanvasGenerator.tiers("s", xlim=xlim, abc=False)
#       if n > 1:  # User also passed the xs
#           cv.paint.signal(args[0], args[1], ylim=ylim, label=label, ylabel=ylabel, xlabel=xlabel)
#       else:
#           cv.paint.signal(args[0], ylim=ylim, label=label, ylabel=ylabel, xlabel=xlabel)
#           
#           ## 2D Array
#   if args[0].ndim in [2, 3]:
#       M = args[0]
#       cv = CanvasGenerator.tiers("m", fig_width=5, xlim=xlim, abc=False)
#       if n == 1:
#           cv.paint.image(M, ylim=ylim, label=label, ylabel=ylabel, xlabel=xlabel)
#       elif n == 2:  # User also passed the xs
#           cv.paint.image(M, args[1], ylim=ylim, label=label, ylabel=ylabel, xlabel=xlabel)
#       elif n == 3:
#           cv.paint.image(args[0], args[1], args[2], ylim=ylim, label=label, ylabel=ylabel, xlabel=xlabel)
#           
#   if label is not None:
#       cv.legend(inside_tile=True)
#       
#   return cv