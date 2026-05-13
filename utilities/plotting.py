"""Diagnostic plots for individual scenarios and lockdown summaries."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .paths import OUTPUT_DIR
from .variants import VARIANT_LABELS, VARIANT_MAP


def save_diagnostic_plots(
    label: str,
    overflow_days: list,
    beds_and_days: list,
    perc_vacant: list,
    summary: dict,
    total_beds: int = None,
) -> None:
    """Saves three diagnostic plots for a scenario to test_images/.

    The three plots are: beds vs days, overflow day histogram, and percent vacant beds histogram.

    :param label: used in titles and output filenames
    :param overflow_days: first-overflow days from each run that overflowed
    :param beds_and_days: list of (beds, days) tuples from each simulation run
    :param perc_vacant: vacancy percentages at simulation end
    :param summary: stats dict returned by report_stats()
    :param total_beds: used to set the y-axis upper limit (optional)
    """
    safe = label.replace(" ", "_")
    n = len(beds_and_days)
    # make individual lines more transparent when there are more runs
    alpha = float(np.clip(50.0 / n, 0.04, 0.5))

    fig, ax = plt.subplots(figsize=(8, 5))
    for beds, days in beds_and_days:
        ax.plot(days, beds, alpha=alpha, linewidth=0.5, color="steelblue")
    ax.set_xlabel("Number of Days")
    ax.set_ylabel("Available Beds")
    ax.set_title(f"{label}: Available Number of Beds")
    if total_beds is not None:
        ax.set_ylim(0, total_beds * 1.05)
    else:
        ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-beds-vs-days.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ov = summary["overflow"]
    if overflow_days:
        ax.hist(overflow_days, bins=10, color="steelblue", edgecolor="white")
        ax.axvline(ov["mean"], color="crimson", linestyle="--", linewidth=1.5,
                   label=f"Mean = {ov['mean']:.1f} d")
        ax.axvspan(ov["ci95"][0], ov["ci95"][1], alpha=0.15, color="crimson",
                   label=f"95% CI  [{ov['ci95'][0]:.1f}, {ov['ci95'][1]:.1f}]")
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.5, "No overflow events", transform=ax.transAxes,
                ha="center", va="center", fontsize=13, color="seagreen",
                fontweight="bold")
    ax.set_xlabel("Day of First Bed Overflow")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{label}: First Day Beds Reach Zero  "
                 f"(P={ov['prob_overflow']:.1%})")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-overflow-hist.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    vs = summary["vacancy"]
    ax.hist(perc_vacant, bins=15, color="steelblue", edgecolor="white")
    ax.axvline(vs["mean"], color="crimson", linestyle="--", linewidth=1.5,
               label=f"Mean = {vs['mean']:.2f}%")
    if not (np.isnan(vs["ci95"][0]) or vs["ci95"][0] == vs["ci95"][1]):
        ax.axvspan(vs["ci95"][0], vs["ci95"][1], alpha=0.15, color="crimson",
                   label=f"95% CI  [{vs['ci95'][0]:.2f}%, {vs['ci95'][1]:.2f}%]")
    ax.legend(fontsize=8)
    ax.set_xlabel("% Vacant Beds at Simulation End")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{label}: Percent Vacant Beds")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-vacancy-hist.png", dpi=150)
    plt.close(fig)

    print(f"  Plots saved -> {OUTPUT_DIR / safe}-*.png")


def plot_flu_infections(trajectories: list, label: str, n_days: int) -> None:
    """Plots active flu infections over time with mean and 5-95 percentile band."""
    fig, ax = plt.subplots(figsize=(9, 5))
    days = np.arange(n_days)

    n = len(trajectories)
    alpha_trial = float(np.clip(50.0 / n, 0.05, 0.4))

    for traj in trajectories:
        ax.plot(days, traj["I"], alpha=alpha_trial, linewidth=0.6, color="forestgreen")

    I_arr  = np.array([t["I"] for t in trajectories])
    mean_I = I_arr.mean(axis=0)
    p5_I   = np.percentile(I_arr, 5, axis=0)
    p95_I  = np.percentile(I_arr, 95, axis=0)

    ax.plot(days, mean_I, color="darkgreen", linewidth=2.5, label="Mean")
    ax.fill_between(days, p5_I, p95_I, alpha=0.18, color="darkgreen",
                    label="5-95 percentile")

    ax.set_xlabel("Day")
    ax.set_ylabel("Active Infections (I)")
    ax.set_title(f"{label}: Active Influenza Infections over Time")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=9)
    fig.tight_layout()

    out = OUTPUT_DIR / f"{label.replace(' ', '_')}-active-infections.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved -> {out.name}")


def plot_flu_infection_proportion(
    trajectories: list,
    label: str,
    n_days: int,
    population: int,
) -> None:
    """Plots flu infections as a fraction of the total population over time."""
    fig, ax = plt.subplots(figsize=(9, 5))
    days = np.arange(n_days)

    n = len(trajectories)
    alpha_trial = float(np.clip(50.0 / n, 0.05, 0.4))

    prop_arr = np.array([t["I"] for t in trajectories]) / population * 100.0

    for prop in prop_arr:
        ax.plot(days, prop, alpha=alpha_trial, linewidth=0.6, color="steelblue")

    mean_p = prop_arr.mean(axis=0)
    p5_p   = np.percentile(prop_arr, 5,  axis=0)
    p95_p  = np.percentile(prop_arr, 95, axis=0)

    ax.plot(days, mean_p, color="navy", linewidth=2.5, label="Mean")
    ax.fill_between(days, p5_p, p95_p, alpha=0.18, color="navy",
                    label="5-95 percentile")

    ax.set_xlabel("Day")
    ax.set_ylabel("Infected Proportion (% of population)")
    ax.set_title(f"{label}: Influenza Infection Proportion over Time")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9)
    fig.tight_layout()

    out = OUTPUT_DIR / f"{label.replace(' ', '_')}-infection-proportion.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved -> {out.name}")


def plot_flu_lockdown_comparison(
    trajectories_by_lockdown: dict,
    label: str,
    n_days: int,
    population: int,
) -> None:
    """3-panel plot comparing flu infection dynamics across lockdown levels.

    Shows active infections, infection proportion, and cumulative attack rate side by side for each lockdown level.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    days = np.arange(n_days)
    colors = {0.0: "crimson", 0.25: "darkorange", 0.5: "forestgreen"}

    for lockdown in sorted(trajectories_by_lockdown.keys()):
        trajs = trajectories_by_lockdown[lockdown]
        color = colors.get(lockdown, "gray")
        legend = f"{int(lockdown * 100)}% lockdown"

        I_arr = np.array([t["I"] for t in trajs])
        ax1.plot(days, I_arr.mean(axis=0), color=color, linewidth=2, label=legend)
        ax1.fill_between(days,
                         np.percentile(I_arr, 5, axis=0),
                         np.percentile(I_arr, 95, axis=0),
                         color=color, alpha=0.15)

        prop_arr = I_arr / population * 100.0
        ax2.plot(days, prop_arr.mean(axis=0), color=color, linewidth=2, label=legend)
        ax2.fill_between(days,
                         np.percentile(prop_arr, 5, axis=0),
                         np.percentile(prop_arr, 95, axis=0),
                         color=color, alpha=0.15)

        # cumulative attack rate = fraction of population no longer susceptible
        S_arr = np.array([t["S"] for t in trajs])
        attack_arr = (1.0 - S_arr / population) * 100.0
        ax3.plot(days, attack_arr.mean(axis=0), color=color, linewidth=2, label=legend)
        ax3.fill_between(days,
                         np.percentile(attack_arr, 5, axis=0),
                         np.percentile(attack_arr, 95, axis=0),
                         color=color, alpha=0.15)

    for ax, ylabel, title in (
        (ax1, "Active Infections (I)",                 "Active Infections"),
        (ax2, "Infected Proportion (% of population)", "Infection Proportion"),
        (ax3, "Cumulative Attack Rate (%)",            "Cumulative Attack Rate"),
    ):
        ax.set_xlabel("Day")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(bottom=0)
        ax.legend(fontsize=9)

    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    fig.suptitle("Influenza Only -- Lockdown Comparison",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()

    out = OUTPUT_DIR / f"{label.replace(' ', '_')}-lockdown-comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved -> {out.name}")


def plot_lockdown_experiments(results: dict, total_beds: int) -> None:
    """Saves H3 bar charts showing overflow probability and bed vacancy by lockdown level.

    Produces three figures: flu-only baseline, COVID-only by variant, and COVID + influenza by variant.
    """
    flu_only   = results["flu_only"]
    covid_only = results["covid_only"]
    dual       = results["dual"]

    levels   = [r["compliance"] for r in flu_only]
    x_pos    = list(range(len(levels)))
    x_labels = [f"{int(L * 100)}%" for L in levels]

    def _bars(ax, data, color, ylabel, title, ylim=None, fmt="{:.2f}"):
        """Helper to draw a simple bar chart with value labels."""
        bars = ax.bar(x_pos, data, color=color, alpha=0.75,
                      edgecolor="black", linewidth=0.5)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel("Lockdown Level")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if ylim is not None:
            ax.set_ylim(*ylim)
        for rect, v in zip(bars, data):
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(),
                    fmt.format(v), ha="center", va="bottom", fontsize=8)

    def _bars_err(ax, mean, lo, hi, color, ylabel, title, ylim=None):
        """Helper to draw a bar chart with 95% CI error bars."""
        err_lo = [max(m - l, 0) for m, l in zip(mean, lo)]
        err_hi = [max(h - m, 0) for m, h in zip(mean, hi)]
        ax.bar(x_pos, mean, yerr=[err_lo, err_hi], color=color, alpha=0.75,
               edgecolor="black", linewidth=0.5, capsize=5)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel("Lockdown Level")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if ylim is not None:
            ax.set_ylim(*ylim)
        for i, m in enumerate(mean):
            ax.text(i, m, f"{m:.1f}", ha="center", va="bottom", fontsize=8)

    # flu-only baseline figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    _bars(ax1,
          [r["overflow"]["prob_overflow"] for r in flu_only],
          "forestgreen", "Overflow Probability", "Overflow Probability",
          ylim=(0, 1.05))
    _bars_err(ax2,
              [r["vacancy"]["mean"]    for r in flu_only],
              [r["vacancy"]["ci95"][0] for r in flu_only],
              [r["vacancy"]["ci95"][1] for r in flu_only],
              "forestgreen", "Mean Vacancy %", "Bed Vacancy at Day 60",
              ylim=(0, 105))
    fig.suptitle("Influenza Only -- Lockdown Impact Baseline (No COVID)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    out = OUTPUT_DIR / "H3_lockdown_flu_only.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved -> {out.name}")

    # COVID-only and dual figures, one column per variant
    variant_colors = {"original": "steelblue", "delta": "crimson",
                      "omicron":  "darkorange"}
    for category_key, category_data in [
        ("covid_only", covid_only), ("dual", dual)
    ]:
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        for col, vname in enumerate(VARIANT_MAP):
            results_v  = category_data[vname]
            color      = variant_colors[vname]

            _bars(axes[0, col],
                  [r["overflow"]["prob_overflow"] for r in results_v],
                  color, "Overflow Probability", VARIANT_LABELS[vname],
                  ylim=(0, 1.05))
            _bars_err(axes[1, col],
                      [r["vacancy"]["mean"]    for r in results_v],
                      [r["vacancy"]["ci95"][0] for r in results_v],
                      [r["vacancy"]["ci95"][1] for r in results_v],
                      color, "Mean Vacancy %", "", ylim=(0, 105))

        title = "COVID-only" if category_key == "covid_only" else "COVID + Influenza"
        fig.suptitle(
            f"{title} -- Lockdown Impact (3 Variants x Lockdown Levels)",
            fontsize=12, fontweight="bold",
        )
        fig.tight_layout()
        out = OUTPUT_DIR / f"H3_lockdown_{category_key}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  Saved -> {out.name}")
