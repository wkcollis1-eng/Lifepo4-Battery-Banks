#!/usr/bin/env python3
"""
outage_analysis.py - the 2026-07-04/05 grid outage, and the coincident-peak
failure mode that ended it.

Reads only files that ship in this repository:

    data/high_freq_voltage/voltage_data_2026-06-17_to_2026-07-16.csv.gz
    data/sem/sem_whole_home_hourly_2026-07-03_2026-07-07.csv
    data/sem/circuit_peaks_*.csv
    data/sem/coincident_peaks_*.csv
    data/sem/events/fridge_coffee_worst_*.csv

Writes figures to figures/ and prints the numbers quoted in
reports/LiFePO4_Report_2026-08-26.md sections 4.1 and 4.2.

Run:  python scripts/outage_analysis.py
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
CRITICAL = "#d03b3b"
ET = "America/New_York"

CAPACITY_AH = 397.0
PLATEAU_MV_PER_PCT = 6.0
INVERTER_W = 1500.0  # Giandel nameplate
SHUNT_R0 = 2.63e-3  # ohmic, commissioning S5.2

# The event, in local time. Times are read off the Shelly trace itself.
GRID_LOSS = pd.Timestamp("2026-07-04 20:50:38", tz=ET)  # UPS on_battery
LOAD_ON = pd.Timestamp("2026-07-04 21:48:58", tz=ET)  # bank picks up the house
CHG_ON = pd.Timestamp("2026-07-05 08:53:56", tz=ET)  # charger starts
CHG_PEAK = pd.Timestamp("2026-07-05 11:35:20", tz=ET)

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


def load_shelly():
    p = DATA / "high_freq_voltage" / "voltage_data_2026-06-17_to_2026-07-16.csv.gz"
    d = pd.read_csv(p)
    d = d[pd.to_numeric(d["state"], errors="coerce").notna()].copy()
    d["v"] = d["state"].astype(float)
    d["t"] = pd.to_datetime(
        d["last_changed"], utc=True, format="ISO8601"
    ).dt.tz_convert(ET)
    return d[["t", "v"]].sort_values("t").reset_index(drop=True)


# ---------------------------------------------------------------------------
def outage(d):
    print("=" * 74)
    print("THE 2026-07-04/05 OUTAGE - the study's only unplanned discharge")
    print("=" * 74)
    pre = d[(d.t >= LOAD_ON - pd.Timedelta("10h")) & (d.t < LOAD_ON)]
    out = d[(d.t >= LOAD_ON) & (d.t < CHG_ON)]
    rest = d[(d.t >= pd.Timestamp("2026-07-05 08:24", tz=ET)) & (d.t < CHG_ON)]
    hours = (CHG_ON - LOAD_ON).total_seconds() / 3600

    i = int(np.argmin(np.abs((d.t - LOAD_ON).dt.total_seconds().to_numpy())))
    step_mV = (d.v[i] - d.v[i - 1]) * 1000
    print(f"  grid loss (UPS on_battery)  {GRID_LOSS:%Y-%m-%d %H:%M:%S} ET")
    print(
        f"  bank picks up the house     {LOAD_ON:%H:%M:%S} ET   "
        f"= {(LOAD_ON - GRID_LOSS).total_seconds() / 60:.0f} min later"
    )
    print(
        f"     load step {d.v[i - 1]:.2f} -> {d.v[i]:.2f} V in "
        f"{(d.t[i] - d.t[i - 1]).total_seconds():.0f} s  ({step_mV:+.0f} mV)"
    )
    print(f"  charger starts              {CHG_ON:%H:%M:%S} ET")
    print(f"  BANK CARRIED THE LOAD FOR   {hours:.2f} h ({hours * 60:.0f} min)")
    print(
        f"\n  pre-outage rested plateau   {pre.v.mean():.4f} V "
        f"(sd {pre.v.std() * 1000:.1f} mV, n={len(pre)})"
    )
    print(
        f"  under load: min {out.v.min():.2f}  p5 {out.v.quantile(0.05):.2f}  "
        f"p95 {out.v.quantile(0.95):.2f}  max {out.v.max():.2f} V  n={len(out)}"
    )

    print("\n  ALARM MARGINS - none approached:")
    for thr, lab in (
        (12.40, "Warning"),
        (12.20, "Critical/BUVL"),
        (11.80, "EMERGENCY"),
    ):
        print(
            f"    {lab:15s} {thr:.2f} V   worst {out.v.min():.2f} V   "
            f"margin {(out.v.min() - thr) * 1000:+5.0f} mV"
        )

    # energy, by delta-OCV rested-to-rested
    x = (rest.t - rest.t.iloc[0]).dt.total_seconds().to_numpy() / 60
    slope = np.polyfit(x, rest.v.to_numpy(), 1)[0]
    lo, hi = rest.v.iloc[-1], rest.v.iloc[-1] + slope * 20
    print("\n  ENERGY [D] by delta-OCV (rested-to-rested, NOT depression under load):")
    print(
        f"    30-min rest after: {rest.v.iloc[0]:.2f} -> {rest.v.iloc[-1]:.2f} V, "
        f"still rising {slope * 60:+.3f} mV/min; charger cut it short at 08:53"
    )
    for lab, vi in (("upper", lo), ("lower", hi)):
        dv = (pre.v.mean() - vi) * 1000
        ah = dv / PLATEAU_MV_PER_PCT / 100 * CAPACITY_AH
        print(
            f"    {lab:6s} dOCV {dv:5.1f} mV -> {dv / PLATEAU_MV_PER_PCT:4.1f} %SOC "
            f"-> {ah:5.1f} Ah -> {ah * 13.1 / 1000:.2f} kWh"
        )
    dv_mid = (pre.v.mean() - (lo + hi) / 2) * 1000
    ah_mid = dv_mid / PLATEAU_MV_PER_PCT / 100 * CAPACITY_AH
    print(
        f"    mean load over {hours:.2f} h: {ah_mid * 13.1 / hours:.0f} W at the bank"
    )
    print("    LIMITS: plateau slope measured at 76-81% SOC, applied ~100->80% where")
    print("    the curve is steeper (Ah overstated); rest cut short at 30 min when 95%")
    print("    relaxation needs 34; Shelly quantises 10 mV = 6.6 Ah per code; and a")
    print("    5.07 h telemetry gap sits mid-event. The INA228 would have returned")
    print("    this directly to 0.15% with no model - this outage IS the argument.")

    g = d[
        (d.t >= pd.Timestamp("2026-07-05 02:00", tz=ET))
        & (d.t <= pd.Timestamp("2026-07-05 09:00", tz=ET))
    ].reset_index(drop=True)
    dt = g.t.diff().dt.total_seconds()
    for j in dt[dt > 600].index:
        print(
            f"\n  TELEMETRY GAP {g.t[j - 1]:%m-%d %H:%M:%S} -> {g.t[j]:%H:%M:%S} ET"
            f" = {dt[j] / 3600:.2f} h  (HA host down; recorder stopped)"
        )
    return pre.v.mean(), out


def fig_outage(d, rested):
    w = d[
        (d.t >= pd.Timestamp("2026-07-04 20:00", tz=ET))
        & (d.t <= pd.Timestamp("2026-07-05 12:30", tz=ET))
    ]
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    # Break the line across the telemetry gap. Without this matplotlib joins
    # the last pre-gap sample to the first post-gap one and the 5 h hole reads
    # as a flat, well-behaved trace - the opposite of the truth.
    ww = w.copy()
    brk = ww["t"].diff().dt.total_seconds() > 600
    ww.loc[brk, "v"] = np.nan
    ax.plot(ww.t, ww.v, lw=1.5, color=C1)
    ax.axhline(rested, lw=1.0, color=MUTED, ls=":")
    ax.annotate(
        f"rested plateau {rested:.3f} V",
        (w.t.iloc[0], rested),
        xytext=(6, 5),
        textcoords="offset points",
        fontsize=8,
        color=INK2,
    )
    for thr, lab, col in (
        (12.40, "Warning 12.40 V", CRITICAL),
        (12.20, "Critical / BUVL 12.20 V", CRITICAL),
    ):
        ax.axhline(thr, lw=1.1, color=col, ls="--", alpha=0.75)
        ax.annotate(
            lab,
            (w.t.iloc[-1], thr),
            xytext=(-6, 5),
            textcoords="offset points",
            ha="right",
            fontsize=8,
            color=col,
        )
    for t, lab, dy in (
        (GRID_LOSS, "grid fails", 40),
        (LOAD_ON, "bank picks up\nthe house", 18),
        (CHG_ON, "charger on", 40),
    ):
        ax.axvline(t, lw=1.0, color=MUTED, ls="-", alpha=0.5)
        ax.annotate(
            lab,
            (t, 12.15),
            xytext=(4, dy),
            textcoords="offset points",
            fontsize=8,
            color=INK2,
        )
    ax.axvspan(
        pd.Timestamp("2026-07-05 03:20:23", tz=ET),
        pd.Timestamp("2026-07-05 08:24:18", tz=ET),
        color=MUTED,
        alpha=0.12,
    )
    ax.annotate(
        "5.07 h telemetry gap\n(HA host down)",
        (pd.Timestamp("2026-07-05 05:52", tz=ET), 12.45),
        ha="center",
        fontsize=8,
        color=INK2,
    )
    ax.annotate(
        "inverter fuses blow ~06:00-07:00\n"
        "fridge + coffee maker inrush\n"
        "INSIDE the blind window - no data",
        (pd.Timestamp("2026-07-05 05:52", tz=ET), 13.9),
        ha="center",
        fontsize=8,
        color=CRITICAL,
    )
    ax.set_ylim(12.0, 14.8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=w.t.dt.tz))
    style(
        ax,
        "2026-07-04/05 outage: the bank carried the house for 11.08 hours",
        "Volts (Shelly)",
        "Time, ET",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIG / "fig_outage_2026-07-04.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
def coincident():
    print("\n" + "=" * 74)
    print("THE COINCIDENT-PEAK FAILURE MODE - why the inverter died")
    print("=" * 74)
    cp = pd.read_csv(min((DATA / "sem").glob("circuit_peaks_*.csv")))
    print(cp.to_string(index=False))

    ex = pd.read_csv(min((DATA / "sem").glob("coincident_peaks_*.csv")))
    ex["t"] = pd.to_datetime(ex["time_utc"], utc=True, format="ISO8601").dt.tz_convert(
        ET
    )
    ex["h"] = ex["t"].dt.hour
    days = ex["t"].dt.normalize().nunique()
    print(f"\n  inverter nameplate {INVERTER_W:.0f} W")
    print(f"  2 s samples over nameplate: {len(ex)}  on {days} distinct days")
    for thr in (1500, 2000, 2500, 3000):
        print(f"    > {thr:4d} W : {(ex['sum_W'] > thr).sum():4d}")
    worst = ex.loc[ex["sum_W"].idxmax()]
    print(
        f"\n  WORST SIMULTANEOUS  {worst['sum_W']:.1f} W at {worst['t']:%Y-%m-%d %H:%M:%S ET}"
    )
    print(f"    fridge {worst['fridge_W']:.1f} + coffee {worst['coffee_W']:.1f}")
    print(f"    = {worst['sum_W'] / INVERTER_W:.2f}x the inverter nameplate [D]")
    for eta in (0.87, 0.94):
        dc = worst["sum_W"] / eta
        print(
            f"    at eta {eta:.0%}: {dc:6.0f} W DC = {dc / 12.9:5.0f} A at 12.9 V"
            f"   {'EXCEEDS' if dc / 12.9 > 250 else 'within'} the SUVL -250 A limit"
        )
    inwin = ex["h"].between(5, 7).sum()
    print(
        f"\n  TIMING: {inwin}/{len(ex)} ({inwin / len(ex) * 100:.0f}%) fall in 05:00-07:59"
    )
    print(
        f"    all {(ex['sum_W'] > 2500).sum()} samples over 2500 W are in "
        f"{ex.loc[ex['sum_W'] > 2500, 'h'].min():02d}:00-"
        f"{ex.loc[ex['sum_W'] > 2500, 'h'].max():02d}:59 - the coffee hour"
    )
    return ex, worst


def fig_coincident(ex, worst):
    w = pd.read_csv(min((DATA / "sem" / "events").glob("fridge_coffee_worst_*.csv")))
    w["t"] = pd.to_datetime(w["time_utc"], utc=True, format="ISO8601").dt.tz_convert(ET)
    t0 = w["t"].iloc[0]
    x = (w["t"] - t0).dt.total_seconds()

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3), width_ratios=[1.25, 1])

    ax = axes[0]
    ax.stackplot(
        x,
        w["fridge_W"],
        w["coffee_W"],
        colors=[C1, C2],
        labels=["Fridge", "Coffee maker"],
        edgecolor=SURFACE,
        linewidth=0.4,
    )
    ax.axhline(INVERTER_W, lw=1.6, color=CRITICAL, ls="--")
    ax.annotate(
        f"Giandel nameplate {INVERTER_W:.0f} W",
        (x.iloc[-1], INVERTER_W),
        xytext=(-6, 6),
        textcoords="offset points",
        ha="right",
        fontsize=8,
        color=CRITICAL,
    )
    ax.annotate(
        f"{worst['sum_W']:.0f} W\n{worst['sum_W'] / INVERTER_W:.1f}x nameplate",
        (x.iloc[int(np.argmax(w["fridge_W"] + w["coffee_W"]))], worst["sum_W"]),
        xytext=(8, -6),
        textcoords="offset points",
        fontsize=8,
        color=INK,
    )
    ax.legend(loc="upper left", fontsize=8)
    style(
        ax,
        f"The worst coincidence: {worst['t']:%Y-%m-%d %H:%M ET}",
        "Watts",
        f"Seconds from {t0:%H:%M:%S} ET",
    )

    ax = axes[1]
    hrs = np.arange(24)
    counts = [int((ex["h"] == h).sum()) for h in hrs]
    ax.bar(hrs, counts, color=C1, width=0.75)
    for h in (5, 6, 7):
        ax.patches[h].set_facecolor(C2)
    ax.annotate(
        "the coffee hour", (6, max(counts) * 1.06), ha="center", fontsize=8, color=C2
    )
    ax.set_ylim(0, max(counts) * 1.18)
    ax.set_xticks([0, 6, 12, 18, 23])
    style(
        ax,
        f"When it happens - {len(ex)} exceedances, 45 days",
        "2 s samples over nameplate",
        "Hour of day, ET",
    )

    fig.tight_layout()
    fig.savefig(FIG / "fig_coincident_peaks.png", bbox_inches="tight")
    plt.close(fig)


def sem_outage_note():
    print("\n" + "=" * 74)
    print("WHAT THE SEM COULD AND COULD NOT SEE")
    print("=" * 74)
    d = pd.read_csv(DATA / "sem" / "sem_whole_home_hourly_2026-07-03_2026-07-07.csv")
    d["t"] = pd.to_datetime(d["time_utc"], utc=True, format="ISO8601").dt.tz_convert(ET)
    w = d[
        (d.t >= pd.Timestamp("2026-07-04 18:00", tz=ET))
        & (d.t <= pd.Timestamp("2026-07-05 11:00", tz=ET))
    ]
    prev = None
    for _, r in w.iterrows():
        gap = (
            ""
            if prev is None or (r.t - prev).total_seconds() <= 3600
            else f"   <-- {(r.t - prev).total_seconds() / 3600:.0f} h GAP (HA down)"
        )
        print(f"   {r.t:%m-%d %H:%M}  {r['whole_home_W']:8.1f} W{gap}")
        prev = r.t
    print("""
   sem_whole_home_power is ch16 + ch17 = main_a + main_b, the SERVICE-ENTRANCE
   CTs. With the main open and the panel backfed through the generator
   interlock, no current crosses them - so 0.0 W is CORRECT BEHAVIOUR, not a
   fault, and it brackets the outage from a third instrument.

   It also means whole-home reads 0 W during EVERY outage, by construction.
   The branch CTs sit downstream of the interlock and would still read, which
   is why sensor.backup_essentials_load is the sensor to trust next time.""")


def main():
    warnings.filterwarnings("ignore")
    d = load_shelly()
    rested, _ = outage(d)
    fig_outage(d, rested)
    sem_outage_note()
    ex, worst = coincident()
    fig_coincident(ex, worst)
    print(f"\nFigures written to {FIG}")


if __name__ == "__main__":
    main()
