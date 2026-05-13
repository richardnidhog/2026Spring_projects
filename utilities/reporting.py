"""Markdown summary writer for simulation results."""
import math
from datetime import datetime
from pathlib import Path

from .paths import PROJECT_ROOT


def _fmt_overflow(ov: dict) -> tuple:
    prob = f"{ov['prob_overflow']:.1%}"
    if ov.get("n_overflowed", 0) > 0:
        mean_day = f"{ov['mean']:.1f}"
        ci_day   = f"[{ov['ci95'][0]:.1f}, {ov['ci95'][1]:.1f}]"
    else:
        mean_day = "—"
        ci_day   = "—"
    return prob, mean_day, ci_day


def _fmt_vacancy(vs: dict) -> tuple:
    mean_v = f"{vs['mean']:.2f}%"
    lo, hi = vs["ci95"]
    if math.isnan(lo) or math.isnan(hi) or lo == hi:
        ci_v = "—"
    else:
        ci_v = f"[{lo:.2f}%, {hi:.2f}%]"
    return mean_v, ci_v


def _h1_section(h1: dict, total_beds: int) -> list:
    lines = ["## H1: Bed Doubling under COVID-only Surge (Delta variant)\n",
             "Compares baseline beds vs doubled beds, no lockdown.\n",
             "| Scenario | Beds | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for label, key, beds in [("Before", "before", total_beds),
                             ("After",  "after",  total_beds * 2)]:
        s = h1[key]
        prob, mean_d, ci_d = _fmt_overflow(s["overflow"])
        mean_v, ci_v       = _fmt_vacancy(s["vacancy"])
        lines.append(f"| {label} | {beds:,} | {prob} | {mean_d} | {ci_d} | {mean_v} | {ci_v} |")
    lines.append("")
    return lines


def _h2_section(h2: dict, total_beds: int) -> list:
    lines = ["## H2: Bed Doubling under COVID + Influenza (Delta variant, doubled beds)\n",
             f"Both scenarios at {total_beds * 2:,} beds, no lockdown.\n",
             "| Scenario | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |",
             "|---|---:|---:|---:|---:|---:|"]
    for label, key in [("COVID-only",  "covid_only"),
                       ("COVID + Flu", "dual")]:
        s = h2[key]
        prob, mean_d, ci_d = _fmt_overflow(s["overflow"])
        mean_v, ci_v       = _fmt_vacancy(s["vacancy"])
        lines.append(f"| {label} | {prob} | {mean_d} | {ci_d} | {mean_v} | {ci_v} |")
    lines.append("")
    return lines


def _h3_lockdown_table(rows: list) -> list:
    """Build a 3-row markdown table (one row per lockdown level)."""
    lines = [
        "| Lockdown | Overflow Probability | Mean Overflow Day | 95 % CI | Mean Vacancy % | 95 % CI |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        prob, mean_d, ci_d = _fmt_overflow(r["overflow"])
        mean_v, ci_v       = _fmt_vacancy(r["vacancy"])
        pct = int(r["compliance"] * 100)
        lines.append(f"| {pct}% | {prob} | {mean_d} | {ci_d} | {mean_v} | {ci_v} |")
    lines.append("")
    return lines


def _h3_section(h3: dict) -> list:
    lines = ["## H3: Lockdown Impact (3 categories × 3 lockdown levels)\n"]

    lines.append("### Influenza-only baseline (no COVID)\n")
    lines.extend(_h3_lockdown_table(h3["flu_only"]))

    lines.append("### COVID-only by variant\n")
    for vname in ("original", "delta", "omicron"):
        if vname in h3.get("covid_only", {}):
            lines.append(f"#### {vname.capitalize()}\n")
            lines.extend(_h3_lockdown_table(h3["covid_only"][vname]))

    lines.append("### COVID + Influenza by variant\n")
    for vname in ("original", "delta", "omicron"):
        if vname in h3.get("dual", {}):
            lines.append(f"#### {vname.capitalize()}\n")
            lines.extend(_h3_lockdown_table(h3["dual"][vname]))

    diag = h3.get("diagnostics") or {}
    if diag:
        lines.append("### Per-scenario diagnostics\n")

        # Omicron
        s = diag.get("omicron_only")
        if s is not None and "overflow" in s:
            prob, mean_d, ci_d = _fmt_overflow(s["overflow"])
            mean_v, ci_v       = _fmt_vacancy(s["vacancy"])
            lines.append("**Omicron-only at lockdown = 0 %** (worst-case COVID surge)")
            lines.append("")
            lines.append(f"- Overflow probability: {prob}")
            lines.append(f"- Mean overflow day: {mean_d}  (95 % CI {ci_d})")
            lines.append(f"- Mean vacancy: {mean_v}  (95 % CI {ci_v})")
            lines.append("")

        # Flu
        flu = diag.get("flu_only")
        if isinstance(flu, dict) and flu:
            lines.append("**Flu-only — infection dynamics across lockdown levels**")
            lines.append("")
            lines.append("| Lockdown | Attack Rate | Attack Rate 5-95 band | "
                         "Peak Active I | Peak Day |")
            lines.append("|---:|---:|---:|---:|---:|")
            for lockdown in sorted(flu.keys()):
                f = flu[lockdown]
                ar      = f"{f['attack_rate_pct']:.4f}%"
                ar_band = f"[{f['attack_rate_p5']:.4f}%, {f['attack_rate_p95']:.4f}%]"
                peak_i  = f"{int(f['peak_infections']):,}"
                peak_d  = f"{f['peak_day_mean']:.1f}"
                lines.append(f"| {int(lockdown * 100)}% | {ar} | {ar_band} | "
                             f"{peak_i} | {peak_d} |")
            lines.append("")

    return lines


def _outputs_section(all_results: dict) -> list:
    lines = ["## Output files\n",
             "All plot files are in `test_images/`.  Generated this run:\n"]
    if "h1" in all_results:
        lines.append("- **H1**: `H1_before-{beds-vs-days,overflow-hist,vacancy-hist}.png`, `H1_after-*.png`")
    if "h2" in all_results:
        lines.append("- **H2**: `H2_covid_only_delta-*.png`, `H2_dual_pathogen_delta-*.png`")
    if "h3" in all_results:
        lines.append("- **H3 summaries**: `H3_lockdown_flu_only.png`, "
                     "`H3_lockdown_covid_only.png`, `H3_lockdown_dual.png`")
        lines.append("- **H3 Omicron diagnostics**: "
                     "`H3_omicron_only-{beds-vs-days,overflow-hist,vacancy-hist}.png`")
        lines.append("- **H3 Flu diagnostics**: `H3_flu_only-active-infections.png`, "
                     "`H3_flu_only-infection-proportion.png`, "
                     "`H3_flu_only-lockdown-comparison.png`")
    lines.append("")
    return lines


def write_markdown_summary(
    all_results: dict,
    config: dict,
    runtime_s: float,
    output_path=None,
) -> Path:

    out = Path(output_path) if output_path is not None else PROJECT_ROOT / "simulation_summary.md"

    lines: list = []
    lines.append("# Hospital Bed Monte Carlo Simulation — Results Summary\n")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("**Configuration**:\n")
    lines.append(f"- Population: {config['population']:,}")
    lines.append(f"- Total beds: {config['total_beds']:,}")
    lines.append(f"- Simulation days: {config['n_days']}")
    lines.append(f"- Monte Carlo runs per scenario: {config['n_simulations']}")
    lines.append(f"- Multiprocessing: {'enabled' if config['do_threading'] else 'disabled'}")
    lines.append(f"- Total runtime: {runtime_s:.1f} seconds")
    lines.append("")
    lines.append("---\n")

    if "h1" in all_results:
        lines.extend(_h1_section(all_results["h1"], config["total_beds"]))
        lines.append("---\n")
    if "h2" in all_results:
        lines.extend(_h2_section(all_results["h2"], config["total_beds"]))
        lines.append("---\n")
    if "h3" in all_results:
        lines.extend(_h3_section(all_results["h3"]))
        lines.append("---\n")

    lines.extend(_outputs_section(all_results))

    out.write_text("\n".join(lines), encoding="utf-8")
    return out
