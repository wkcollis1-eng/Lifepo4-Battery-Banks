#!/usr/bin/env python3
"""
ina228_analysis.py - reproduce every INA228-era figure and headline number.

Reads only files that ship in this repository (see data/README.md), so the
analysis is reproducible without access to the Home Assistant host:

    data/ina228/ina228_daily_*.csv          daily aggregates
    data/ina228/ina228_hourly_*.csv         hourly aggregates
    data/ina228/stasis_ma60_*.csv.gz        1-minute MA-60s voltage means
    data/ina228/events/*.csv[.gz]           2 s resolution, event windows
    data/Shelly Voltage.csv                 Shelly, commissioning overlap
    data/high_freq_voltage/voltage_data_2026-06-17_to_2026-07-16.csv.gz
    data/shelly_daily_min_2026-04-01_2026-07-16.csv

Writes figures to figures/ and prints the numbers quoted in
reports/LiFePO4_Report_2026-08-26.md.

Run:  python scripts/ina228_analysis.py
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
INA = DATA / "ina228"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# Validated categorical slots 1-3 (see the project's data-viz palette).
# All-pairs CVD dE 9.2, normal-vision dE 24.0 on the light surface.
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
CRITICAL = "#d03b3b"

ANCHOR = pd.Timestamp("2026-07-16 19:50:00", tz="UTC")  # charger stop / SOC anchor
CAPACITY_AH = 397.0  # Oct 2025 discharge test
PLATEAU_MV_PER_PCT = 6.0  # bank OCV plateau slope, commissioning report S5.3

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK2,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 130,
    }
)


def style(ax, title=None, ylabel=None, xlabel=None):
    if title:
        ax.set_title(title, color=INK, loc="left", pad=8)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_axisbelow(True)
    return ax


def read_ts(path, index=True):
    """Read a repo CSV whose first column is an ISO UTC timestamp."""
    d = pd.read_csv(path)
    # format="ISO8601": whole-second timestamps are written without the
    # fractional part, so the column is not one fixed strptime format.
    d["time_utc"] = pd.to_datetime(d["time_utc"], utc=True, format="ISO8601")
    return d.set_index("time_utc") if index else d


def load_ina():
    daily = read_ts(min(INA.glob("ina228_daily_*.csv")))
    hourly = read_ts(min(INA.glob("ina228_hourly_*.csv")))
    ma = read_ts(min(INA.glob("stasis_ma60_*.csv*")))
    return daily, hourly, ma


# ---------------------------------------------------------------------------
# 1. Post-charge relaxation and the stasis noise floor
# ---------------------------------------------------------------------------
def fig_relaxation(ma):
    d = ma["v_ma60s_mean"].dropna()
    t = (d.index - ANCHOR).total_seconds().to_numpy() / 86400.0
    y = d.to_numpy()

    def two_exp(x, vinf, a1, t1, a2, t2):
        return vinf + a1 * np.exp(-x / t1) + a2 * np.exp(-x / t2)

    p, _cov = optimize.curve_fit(
        two_exp, t, y, p0=[13.30, 0.30, 0.05, 0.62, 3.0], maxfev=200000
    )
    resid = y - two_exp(t, *p)

    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.6), height_ratios=[1.35, 1])

    ax = axes[0]
    ax.plot(t, y, lw=1.6, color=C1, label="Bank voltage, MA-60s")
    ax.plot(t, two_exp(t, *p), lw=1.4, color=C2, ls="--", label="Two-exponential fit")
    ax.axhline(p[0], lw=1.0, color=MUTED, ls=":")
    ax.annotate(
        f"fitted asymptote {p[0]:.4f} V",
        (t[-1], p[0]),
        xytext=(-6, 7),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=INK2,
    )
    ax.annotate(
        f"tau1 = {p[2] * 24:.1f} h\ntau2 = {p[4]:.2f} d",
        (2.0, 13.72),
        fontsize=8,
        color=INK2,
    )
    ax.set_xlim(0, t[-1])
    ax.legend(loc="upper right", fontsize=8)
    style(ax, "Post-charge relaxation, 2026-07-16 charger stop to 2026-08-26", "Volts")

    ax = axes[1]
    ax.semilogy(t, np.abs(resid) * 1000 + 1e-3, lw=0.8, color=C3, alpha=0.85)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(1e-2, 1e3)
    style(ax, "Fit residual, absolute", "mV  (log)", "Days since charger stop")
    ax.annotate(
        "residual sd "
        f"{resid.std() * 1000:.1f} mV over the whole span;\n"
        f"{np.abs(resid[t > 14]).max() * 1000:.2f} mV worst case after day 14",
        (0.55, 0.82),
        xycoords="axes fraction",
        fontsize=8,
        color=INK2,
    )

    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_relaxation.png", bbox_inches="tight")
    plt.close(fig)
    return p, resid


def fig_noise_floor(daily):
    d = daily.dropna(subset=["v_sd_mV"])
    d = d[d.index >= ANCHOR.floor("D")]
    t = (d.index - ANCHOR.floor("D")).days
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.semilogy(
        t,
        d["v_sd_mV"],
        lw=1.8,
        color=C1,
        marker="o",
        ms=3.2,
        markerfacecolor=SURFACE,
        markeredgewidth=1.1,
    )
    last = int(t.max())
    for lbl, day, dx, ha in (
        ("day 1", 1, 8, "left"),
        ("day 12", 12, 8, "left"),
        (f"day {last}", last, -8, "right"),
    ):
        if day in list(t):
            v = d["v_sd_mV"].iloc[list(t).index(day)]
            ax.annotate(
                f"{lbl}: {v:.3g} mV",
                (day, v),
                xytext=(dx, 10),
                textcoords="offset points",
                ha=ha,
                fontsize=8,
                color=INK2,
            )
    ax.axhline(0.195, lw=1.0, color=MUTED, ls=":")
    ax.annotate(
        "INA228 bus-voltage LSB, 0.195 mV",
        (1, 0.195),
        xytext=(0, -13),
        textcoords="offset points",
        fontsize=8,
        color=MUTED,
    )
    ax.set_xlim(-1, last + 3)
    style(
        ax,
        "Within-day voltage standard deviation collapses by 2.7 decades",
        "mV  (log)",
        "Days since charger stop",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_noise_floor.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. The directly measured parasitic drain
# ---------------------------------------------------------------------------
def fig_parasitic(daily, hourly):
    d = daily[(daily.index > ANCHOR) & (daily["coverage_s"] > 80000)]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.plot(
        d.index,
        -d["i_timemean_mA"],
        lw=1.8,
        color=C1,
        marker="o",
        ms=3.4,
        markerfacecolor=SURFACE,
        markeredgewidth=1.1,
    )
    step = pd.Timestamp("2026-08-04 18:30", tz="UTC")
    ax.axvline(step, lw=1.2, color=CRITICAL, ls="--")
    ax.annotate(
        "2026-08-04 14:30 ET\nunexplained +2.9 mA step",
        (step, 9.6),
        xytext=(8, 0),
        textcoords="offset points",
        fontsize=8,
        color=CRITICAL,
    )
    ax.axhline(12.5, lw=1.0, color=MUTED, ls=":")
    ax.annotate(
        "Shelly-era estimate, 12.5 mA",
        (d.index[-1], 12.5),
        xytext=(-4, 5),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=MUTED,
    )
    ax.set_ylim(0, 14)
    style(
        ax,
        "Directly measured quiescent drain, daily time-weighted mean",
        "mA drawn from the bank",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_parasitic.png", bbox_inches="tight")
    plt.close(fig)


def fig_coulomb_ledger():
    """Three accountants, one current: silicon, this script, and the firmware."""
    d = read_ts(INA / "coulomb_ledger_hourly.csv")
    d = d[d.index >= pd.Timestamp("2026-07-25 20:00", tz="UTC")]  # last reboot
    for c in ("hw_ah", "own_ah", "sw_net_ah"):
        d[c] = d[c] - d[c].iloc[0]
    t = (d.index - d.index[0]).total_seconds() / 86400.0

    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.plot(
        t,
        d["hw_ah"],
        lw=2.0,
        color=C1,
        label="INA228 CHARGE register, accumulated in silicon",
    )
    ax.plot(
        t,
        d["own_ah"],
        lw=1.4,
        ls="--",
        color=C2,
        label="Independent integration of the published 2 s series",
    )
    ax.plot(
        t,
        d["sw_net_ah"],
        lw=2.0,
        color=C3,
        label="Firmware coulomb ledger (+/-0.05 A deadband)",
    )
    ax.axhline(0, lw=0.8, color=AXIS)
    ax.annotate(
        f"{d['hw_ah'].iloc[-1]:.2f} Ah",
        (t[-1], d["hw_ah"].iloc[-1]),
        xytext=(-8, 6),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=C1,
    )
    ax.set_ylim(-6.4, 0.5)
    ax.annotate(
        f"{d['sw_net_ah'].iloc[-1]:.3f} Ah - the drain sits inside the\n"
        "deadband, so the firmware never counts it",
        (t[-1] * 0.44, -1.4),
        fontsize=8,
        color=INK2,
    )
    ax.legend(loc="lower left", fontsize=8)
    style(
        ax,
        "The same charge, measured three ways, over 32 quiescent days",
        "Cumulative net charge, Ah",
        "Days since the 2026-07-25 reboot",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_coulomb_ledger.png", bbox_inches="tight")
    plt.close(fig)
    return d


# ---------------------------------------------------------------------------
# 3. Charge and discharge characterisation
# ---------------------------------------------------------------------------
def fig_charge(ev):
    d = read_ts(ev)
    t = (d.index - d.index[0]).total_seconds() / 60.0
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.4), sharex=True)

    ax = axes[0]
    ax.plot(t, d["current"], lw=1.6, color=C1)
    ax.axhline(0, lw=0.8, color=AXIS)
    ax.annotate(
        "CC, 78.6 A mean\n(98.3% of the 80 A nameplate)",
        (18, 60),
        fontsize=8,
        color=INK2,
    )
    ax.annotate(
        "taper to 6.48 A cutoff\n(C/77)", (86, 26), fontsize=8, color=INK2, ha="right"
    )
    style(ax, "LiTime 80 A charge, 2026-07-16 - current", "Amps")

    ax = axes[1]
    ax.plot(t, d["voltage"], lw=1.6, color=C2)
    for v, lbl in (
        (14.20, "CV entry, 14.20 V"),
        (14.584, "Vmax 14.584 V"),
        (14.80, "BOVL hardware limit, 14.80 V"),
    ):
        ax.axhline(v, lw=1.0, color=MUTED, ls=":")
        ax.annotate(
            lbl,
            (t.max(), v),
            xytext=(-4, 4),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color=MUTED,
        )
    style(
        ax,
        "LiTime 80 A charge, 2026-07-16 - bus voltage",
        "Volts",
        "Minutes from charge start",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_charge_profile.png", bbox_inches="tight")
    plt.close(fig)


def fig_discharge(events):
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.8))
    titles = [
        "70 W overnight, 15.6 h",
        "1 kW heater, 15.4 min",
        "Inverter nameplate, 11.6 min",
    ]
    colors = [C1, C2, C3]
    for ax, (path, ttl, col) in zip(axes, zip(events, titles, colors)):
        d = read_ts(path)
        t = (d.index - d.index[0]).total_seconds() / 60.0
        ax.plot(t, d["voltage"], lw=1.4, color=col)
        ax.annotate(
            f"Vmin {d['voltage'].min():.3f} V\nIpk {-d['current'].min():.1f} A",
            (0.04, 0.24),
            xycoords="axes fraction",
            fontsize=8,
            color=INK2,
        )
        style(ax, ttl, "Volts" if ax is axes[0] else None, "Minutes")
    for v, lbl in ((12.40, "Warning"), (12.20, "Critical / BUVL")):
        for ax in axes:
            ax.axhline(v, lw=0.9, color=MUTED, ls=":")
    axes[2].annotate("12.40 V Warning", (0.4, 12.42), fontsize=7, color=MUTED)
    axes[2].annotate("12.20 V Critical / BUVL", (0.4, 12.22), fontsize=7, color=MUTED)
    fig.suptitle(
        "Commissioning discharge campaign - bus voltage under three load levels",
        x=0.012,
        ha="left",
        fontsize=11,
        color=INK,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig_ina228_discharge_legs.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Ten-month timeline, both instruments on one scale
# ---------------------------------------------------------------------------
def fig_timeline(daily, delta_mV):
    """delta_mV is (Shelly - INA228), i.e. negative: the Shelly reads low.
    Putting the Shelly on the INA228 scale therefore SUBTRACTS it."""
    # Oct 2025 - Mar 2026: hourly Min/Max exports, so the daily level is the
    # mean of the hourly midpoints. Apr - Jul 2026: only a daily minimum was
    # exported. The two statistics coincide once the bank is in stasis - over
    # Mar 27-31 the hourly Min and Max are the same 10 mV code, so midpoint and
    # minimum are identical - which is what makes the join legitimate here.
    hourly_shelly = pd.read_csv(DATA / "combined_output.csv")
    hourly_shelly["dt"] = pd.to_datetime(
        hourly_shelly["Date"] + " " + hourly_shelly["Time"], format="%d/%m/%Y %H:%M"
    )
    hourly_shelly["mid"] = (hourly_shelly["Min"] + hourly_shelly["Max"]) / 2
    s1 = hourly_shelly.groupby(hourly_shelly["dt"].dt.date)["mid"].mean()
    s1.index = pd.to_datetime(s1.index)

    dmin = pd.read_csv(
        DATA / "shelly_daily_min_2026-04-01_2026-07-16.csv", parse_dates=["date"]
    ).set_index("date")["v_min"]
    shelly = pd.concat([s1, dmin]).sort_index()
    shelly = shelly[~shelly.index.duplicated(keep="last")] - delta_mV / 1000.0

    ina = daily["v_mean"].dropna()
    ina.index = ina.index.tz_localize(None)
    base = 13.270 - delta_mV / 1000.0

    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.plot(
        shelly.index,
        shelly.to_numpy(),
        lw=1.4,
        color=C2,
        label=f"Shelly Plus Uni, daily level, {-delta_mV:+.0f} mV offset applied",
    )
    ax.plot(ina.index, ina.to_numpy(), lw=1.8, color=C1, label="INA228, daily mean")
    ax.axhline(base, lw=1.0, color=MUTED, ls=":")
    ax.annotate(
        f"Nov 2025 stasis baseline on the INA228 scale, {base:.3f} V",
        (0.02, 0.06),
        xycoords="axes fraction",
        fontsize=8,
        color=INK2,
    )
    ax.set_ylim(12.6, 14.0)
    ax.legend(loc="upper right", fontsize=8)
    style(
        ax,
        "Ten months of bank voltage across an instrument change",
        "Volts, INA228 scale",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIG / "fig_ina228_ten_month_timeline.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Shelly / INA228 cross-calibration
# ---------------------------------------------------------------------------
def crosscheck():
    """Shelly-minus-INA228 offset from the published paired dataset.

    The quiescent estimate is gated on BOTH a quiet bank and a still voltage.
    Without the dV/dt gate, pairing a 2 min, 10 mV-quantised instrument to a 2 s
    one during post-charge relaxation measures the relaxation, not the offset -
    it inflates the spread five-fold and biases the mean.
    """
    m = read_ts(INA / "shelly_ina228_crosscheck.csv", index=False)
    m = m.rename(columns={"delta_mV": "d_mV"})
    quiet = m[(m["current_A"].abs() < 0.5) & (m["dvdt_mV_per_min"].abs() < 1)]
    load = m[(m["current_A"] < -5) & (m["dvdt_mV_per_min"].abs() < 5)]

    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    bins = np.arange(-60, -5, 2.5)
    # Step outlines, not translucent fills: overlapping alpha fills produce a
    # third colour that belongs to neither series and reads as a category.
    ax.hist(
        quiet["d_mV"],
        bins=bins,
        density=True,
        histtype="step",
        lw=2,
        color=C1,
        label=f"Bank idle, n={len(quiet)}",
    )
    ax.hist(
        load["d_mV"],
        bins=bins,
        density=True,
        histtype="step",
        lw=2,
        color=C2,
        label=f"Under load, I < -5 A, n={len(load)}",
    )
    ax.axvline(quiet["d_mV"].mean(), lw=1.2, color=C1, ls="--")
    ax.axvline(load["d_mV"].mean(), lw=1.2, color=C2, ls="--")
    top = ax.get_ylim()[1]
    ax.annotate(
        f"idle mean {quiet['d_mV'].mean():.1f} mV",
        (quiet["d_mV"].mean(), top * 0.96),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=C1,
    )
    ax.annotate(
        f"loaded mean {load['d_mV'].mean():.1f} mV",
        (load["d_mV"].mean(), top * 0.86),
        xytext=(6, 0),
        textcoords="offset points",
        fontsize=8,
        color=C2,
    )
    ax.set_xlim(-60, -5)
    ax.legend(loc="upper left", fontsize=8)
    style(
        ax,
        "Shelly reads low against the INA228 - paired samples, 30 s window",
        "Density",
        "Shelly minus INA228, mV",
    )
    fig.tight_layout()
    fig.savefig(FIG / "fig_shelly_ina228_offset.png", bbox_inches="tight")
    plt.close(fig)
    return m, quiet, load


# ---------------------------------------------------------------------------
# 6. Bounding the internal term (self-discharge + BMS standby)
# ---------------------------------------------------------------------------
# Inputs and their 1-sigma uncertainties. The shunt offset dominates the budget
# and is the reason this is a bound rather than a measurement.
TEMPCO_MV_PER_F = (1.0, 0.3)  # system-level, from the Shelly-era study
PLATEAU_SE = 1.0  # on the 6.0 mV/%SOC bank plateau slope
SHUNT_OFFSET_MA = 2.4  # commissioning Tier 2: 0.9 uV at 375 uOhm


def selfdischarge_bound(daily, n_draws=200_000, seed=7):
    """Bound the SOC loss the shunt cannot see, over the clean late window.

    The voltage path measures TOTAL SOC decline; the shunt measures charge
    crossing the terminals. The difference is everything that lowers SOC without
    crossing them - true self-discharge AND the internal BMS standby draw, which
    sits between the cells and the terminals. That bundle is what a pack-level
    datasheet calls "self-discharge", so it compares like-for-like.

    Window is day 34-41 post-charge, where the relaxation tail has decayed below
    0.005 mV/day and cannot contaminate the slope (see fig_ina228_relaxation).
    """
    d = daily[
        (daily.index >= pd.Timestamp("2026-08-19", tz="UTC"))
        & (daily["coverage_s"] > 80000)
    ]
    x = np.arange(len(d))
    r_v = stats.linregress(x, d["v_mean"].to_numpy() * 1000)
    r_t = stats.linregress(x, d["pack_F"].to_numpy())
    dt_i = d["ah_net"].sum() * 3600 / d["coverage_s"].sum() * 1000  # mA, signed

    rng = np.random.default_rng(seed)
    slope = rng.normal(r_v.slope, r_v.stderr, n_draws)  # mV/day, negative
    tempco = rng.normal(*TEMPCO_MV_PER_F, n_draws)
    plateau = rng.normal(PLATEAU_MV_PER_PCT, PLATEAU_SE, n_draws)
    shunt = rng.normal(abs(dt_i), SHUNT_OFFSET_MA, n_draws)

    corrected = slope - r_t.slope * tempco  # remove the thermal component
    total_mA = abs(corrected) / (24 / 1000 / CAPACITY_AH * 100 * plateau)
    internal = total_mA - shunt  # what the shunt cannot see

    def pct_month(ma_):
        return ma_ * 24 / 1000 * 30.44 / CAPACITY_AH * 100

    print(f"  window {d.index[0]:%Y-%m-%d} -> {d.index[-1]:%Y-%m-%d}  n={len(d)} days")
    print(
        f"  observed slope     {r_v.slope:+.4f} mV/day  se {r_v.stderr:.4f}  "
        f"r2 {r_v.rvalue**2:.3f}"
    )
    print(f"  pack temp drift    {r_t.slope:+.4f} degF/day")
    print(
        f"  temp-corrected     {r_v.slope - r_t.slope * TEMPCO_MV_PER_F[0]:+.4f} mV/day"
    )
    print(f"  shunt drain        {abs(dt_i):.2f} mA")
    for label, arr in (
        ("total SOC loss (mA)", total_mA),
        ("INTERNAL term (mA)", internal),
    ):
        q = np.percentile(arr, [2.5, 16, 50, 84, 97.5])
        print(
            f"  {label:22s} median {q[2]:+7.3f}   68% [{q[1]:+.2f},{q[3]:+.2f}]"
            f"   95% [{q[0]:+.2f},{q[4]:+.2f}]"
        )
    ip = pct_month(internal)
    print(
        f"  INTERNAL %SOC/month    median {np.median(ip):+.3f}   "
        f"95th pct {np.percentile(ip, 97.5):+.3f}"
    )
    print(
        f"  P(>2 %/mo) = {(ip > 2).mean() * 100:.2f}%   "
        f"P(>1 %/mo) = {(ip > 1).mean() * 100:.2f}%"
    )
    if np.median(internal) < 0:
        print("  NOTE median is NEGATIVE - physically impossible for self-discharge,")
        print("       which is the diagnostic that systematics exceed the signal.")
        print("       Read the 95th percentile as a ceiling; nothing else.")

    base = abs(r_v.slope - r_t.slope * TEMPCO_MV_PER_F[0]) / (
        24 / 1000 / CAPACITY_AH * 100 * PLATEAU_MV_PER_PCT
    ) - abs(dt_i)
    print("  error budget (1-sigma swing in the internal term):")
    for lab, sl, tc, pl, sh in (
        (
            "shunt offset +-2.4 mA",
            r_v.slope,
            TEMPCO_MV_PER_F[0],
            PLATEAU_MV_PER_PCT,
            abs(dt_i) + SHUNT_OFFSET_MA,
        ),
        (
            "plateau +-1.0 mV/%",
            r_v.slope,
            TEMPCO_MV_PER_F[0],
            PLATEAU_MV_PER_PCT + PLATEAU_SE,
            abs(dt_i),
        ),
        (
            "tempco +-0.3 mV/degF",
            r_v.slope,
            TEMPCO_MV_PER_F[0] + TEMPCO_MV_PER_F[1],
            PLATEAU_MV_PER_PCT,
            abs(dt_i),
        ),
        (
            "regression se",
            r_v.slope + r_v.stderr,
            TEMPCO_MV_PER_F[0],
            PLATEAU_MV_PER_PCT,
            abs(dt_i),
        ),
    ):
        v = abs(sl - r_t.slope * tc) / (24 / 1000 / CAPACITY_AH * 100 * pl) - sh
        print(f"    {lab:24s} internal {v:+6.2f} mA   shift {v - base:+.2f}")
    return internal


def main():
    warnings.filterwarnings("ignore")
    daily, hourly, ma = load_ina()

    print("=" * 74)
    print("COVERAGE")
    print("=" * 74)
    cov = daily["coverage_s"].sum() / 86400
    print(f"  daily rows {len(daily)}   integrated coverage {cov:.2f} days")
    print(f"  window {daily.index[0]:%Y-%m-%d} -> {daily.index[-1]:%Y-%m-%d}")
    print(f"  current samples {int(daily['n_current'].sum()):,}")

    print("\n" + "=" * 74)
    print("STASIS - RELAXATION AND NOISE FLOOR")
    print("=" * 74)
    p, resid = fig_relaxation(ma)
    print(
        f"  V_inf = {p[0]:.4f} V   A1 = {p[1]:+.4f} V  tau1 = {p[2] * 24:.2f} h"
        f"   A2 = {p[3]:+.4f} V  tau2 = {p[4]:.3f} d"
    )
    print(
        f"  residual sd = {resid.std() * 1000:.2f} mV   n = {len(resid):,} minute means"
    )
    fig_noise_floor(daily)
    s = daily[daily.index >= ANCHOR.floor("D")]["v_sd_mV"].dropna()
    print(f"  within-day sd: day 1 {s.iloc[1]:.2f} mV -> final day {s.iloc[-1]:.3f} mV")

    d = daily[(daily.index > ANCHOR) & (daily["coverage_s"] > 80000)]
    print("\n  MA-60s drift, OLS on daily means:")
    for w in (3, 5, 7, 14, 30):
        y = d["v_mean"].iloc[-w:].to_numpy() * 1000
        r = stats.linregress(np.arange(w), y)
        print(
            f"    last {w:2d} d: {r.slope:+7.4f} mV/day  r2={r.rvalue**2:.3f}  "
            f"se={r.stderr:.4f}  p={r.pvalue:.2e}"
        )

    print("\n" + "=" * 74)
    print("PARASITIC DRAIN - DIRECTLY MEASURED")
    print("=" * 74)
    fig_parasitic(daily, hourly)
    ah = d["ah_net"].sum()
    secs = d["coverage_s"].sum()
    print(f"  net over {secs / 86400:.2f} integrated days: {ah:+.4f} Ah")
    print(f"  time-weighted mean: {ah * 3600 / secs * 1000:+.2f} mA")
    print(
        f"  = {abs(ah) / CAPACITY_AH * 100:.3f}% of {CAPACITY_AH:.0f} Ah "
        f"= {abs(ah) / secs * 86400 * 30.44 / CAPACITY_AH * 100:.2f} %/month"
    )
    print(
        f"  daily range {-d['i_timemean_mA'].max():.2f} to "
        f"{-d['i_timemean_mA'].min():.2f} mA"
    )
    pre = d.loc[:"2026-08-04", "i_timemean_mA"].iloc[-5:]
    post = d.loc["2026-08-05":"2026-08-18", "i_timemean_mA"]
    t, pv = stats.ttest_ind(pre, post, equal_var=False)
    print(
        f"  Aug 4 step: {pre.mean():+.2f} mA (n={len(pre)}) -> {post.mean():+.2f} mA "
        f"(n={len(post)})  Welch t={t:.1f}  p={pv:.1e}"
    )

    print("\n  cross-check against the OCV plateau slope:")
    y7 = d["v_mean"].iloc[-7:].to_numpy() * 1000
    drift = stats.linregress(np.arange(7), y7).slope
    print(
        f"    voltage path : {drift:+.3f} mV/day / {PLATEAU_MV_PER_PCT:.1f} mV/%SOC "
        f"= {drift / PLATEAU_MV_PER_PCT * 30.44:+.2f} %SOC/month"
    )
    print(
        f"    coulomb path : {ah / secs * 86400 * 30.44 / CAPACITY_AH * 100:+.2f} %SOC/month"
    )

    print("\n" + "=" * 74)
    print("COULOMB LEDGER - THREE INDEPENDENT ACCOUNTANTS")
    print("=" * 74)
    led = fig_coulomb_ledger()
    span = (led.index[-1] - led.index[0]).total_seconds()
    print(
        f"  window {led.index[0]:%Y-%m-%d %H:%M} -> {led.index[-1]:%Y-%m-%d %H:%M} UTC "
        f"({span / 86400:.2f} d, no reboot)"
    )
    hw, own, sw = (led[c].iloc[-1] for c in ("hw_ah", "own_ah", "sw_net_ah"))
    print(
        f"  INA228 CHARGE register (silicon, 1.58 s)   {hw:+9.4f} Ah  "
        f"= {hw / span * 3600 * 1000:+7.3f} mA"
    )
    print(
        f"  independent integration (2 s left-rect)    {own:+9.4f} Ah  "
        f"= {own / span * 3600 * 1000:+7.3f} mA"
    )
    print(
        f"  firmware ledger (+/-0.05 A deadband)       {sw:+9.4f} Ah  "
        f"= {sw / span * 3600 * 1000:+7.3f} mA"
    )
    print(
        f"  silicon vs independent: {abs(own - hw):.4f} Ah "
        f"({abs(own - hw) / abs(hw) * 100:.2f}%) - integration-method error only"
    )
    print(
        f"  firmware sees {abs(sw) / abs(hw) * 100:.2f}% of the charge the same chip moved"
    )
    print(
        f"  unbooked at the end of the window: {abs(hw - sw):.3f} Ah "
        f"= {abs(hw - sw) / CAPACITY_AH * 100:.2f} %SOC"
    )

    print("\n" + "=" * 74)
    print("CHARGE AND DISCHARGE")
    print("=" * 74)
    fig_charge(INA / "events" / "charge_2026-07-16_litime_80A.csv")
    fig_discharge(
        [
            INA / "events" / f
            for f in (
                "discharge_2026-07-15_70W_overnight.csv.gz",
                "discharge_2026-07-16_1kW_heater.csv",
                "discharge_2026-07-16_inverter_trip.csv",
            )
        ]
    )
    for f in sorted((INA / "events").glob("*.csv*")):
        e = read_ts(f)
        dt = (
            e.index.to_series()
            .diff()
            .shift(-1)
            .dt.total_seconds()
            .fillna(0)
            .clip(0, 10)
        )
        ah = (e["current"] * dt).sum() / 3600
        wh = (e["power"] * dt).sum() / 3600
        dur = (e.index[-1] - e.index[0]).total_seconds() / 60
        print(
            f"  {f.stem:36s} {dur:7.1f} min  {ah:+9.3f} Ah  {wh:+9.2f} Wh  "
            f"Vmin {e['voltage'].min():.4f}  Vmax {e['voltage'].max():.4f}  "
            f"Ipk {e['current'].abs().max():7.2f} A"
        )

    print("\n" + "=" * 74)
    print("SHELLY / INA228 CROSS-CALIBRATION")
    print("=" * 74)
    m, quiet, load = crosscheck()
    for lbl, sub in (
        ("all paired", m),
        ("idle |I|<0.5 A", quiet),
        ("loaded I<-5 A", load),
    ):
        ci = stats.t.interval(
            0.95, len(sub) - 1, loc=sub["d_mV"].mean(), scale=stats.sem(sub["d_mV"])
        )
        print(
            f"  {lbl:16s} n={len(sub):5,}  mean {sub['d_mV'].mean():+7.2f} mV  "
            f"sd {sub['d_mV'].std():5.2f}  95% CI [{ci[0]:+.2f}, {ci[1]:+.2f}]"
        )
    off = quiet["d_mV"].mean()
    fig_timeline(daily, off)
    print(
        f"\n  Nov 2025 baseline 13.270 V (Shelly) -> {13.270 - off / 1000:.3f} V "
        f"on the INA228 scale"
    )
    print(f"  INA228 measured on the final day: {daily['v_mean'].iloc[-1]:.4f} V")

    print("\n" + "=" * 74)
    print("INTERNAL TERM - SELF-DISCHARGE + BMS STANDBY - BOUNDED, NOT MEASURED")
    print("=" * 74)
    selfdischarge_bound(daily)

    print("\n" + "=" * 74)
    print("STORAGE STASIS, Apr 1 - Jul 4 2026 (Shelly daily minima)")
    print("=" * 74)
    dm = pd.read_csv(
        DATA / "shelly_daily_min_2026-04-01_2026-07-16.csv", parse_dates=["date"]
    )
    q = dm[(dm["date"] >= "2026-04-01") & (dm["date"] <= "2026-07-04")]
    x = (q["date"] - q["date"].iloc[0]).dt.days.to_numpy().astype(float)
    r = stats.linregress(x, q["v_min"].to_numpy() * 1000)
    print(
        f"  n={len(q)} days  mean {q['v_min'].mean():.4f} V  "
        f"sd {q['v_min'].std() * 1000:.2f} mV"
    )
    print(
        f"  OLS drift {r.slope:+.4f} mV/day  se {r.stderr:.4f}  "
        f"r2 {r.rvalue**2:.3f}  p {r.pvalue:.3f}"
    )

    print(f"\nFigures written to {FIG}")


if __name__ == "__main__":
    main()
