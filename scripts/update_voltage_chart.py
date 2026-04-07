#!/usr/bin/env python3
"""
update_voltage_chart.py — Regenerates voltage_chart.html from repo data.

Usage (from repo root):
    python scripts/update_voltage_chart.py

Outputs: voltage_chart.html (repo root)

# CLAUDE: When data coverage extends, update the HTML header strings below:
#   - Page title "130-Day Voltage Trend Analysis"     → update day count
#   - Page subtitle date range                        → update end date
#   - "Total Duration" stat card value                → update day count
#   - "Last updated" footer line                      → update date
#   - stats grid values (drift rate, parasitic draw)  → update from latest report
"""

import pandas as pd
import json
import os

# Resolve paths relative to repo root (works from any working directory)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOLTAGE_FILE = os.path.join(REPO_ROOT, "data", "combined_output.csv")
TEMP_FILE = os.path.join(REPO_ROOT, "data", "combined_temperature.csv")
OUTPUT_FILE = os.path.join(REPO_ROOT, "voltage_chart.html")

# Load actual voltage data
df = pd.read_csv(VOLTAGE_FILE)
df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M")
df["avg"] = (df["Min"] + df["Max"]) / 2

# Get daily data
df["date"] = df["datetime"].dt.date
daily = (
    df.groupby("date").agg({"Min": "min", "Max": "max", "avg": "mean"}).reset_index()
)

# Convert to JavaScript array format
voltage_data = []
for _, row in daily.iterrows():
    voltage_data.append(
        {
            "date": str(row["date"]),
            "voltage": round(row["avg"] * 1000, 1),
            "vmax": round(row["Max"] * 1000, 1),
            "vmin": round(row["Min"] * 1000, 1),
        }
    )

# Load temperature data
temp_df = pd.read_csv(TEMP_FILE)
temp_df["datetime"] = pd.to_datetime(
    temp_df["Date"] + " " + temp_df["Time"], format="%d/%m/%Y %H:%M"
)
temp_df["date"] = temp_df["datetime"].dt.date
temp_df["temp_avg"] = (temp_df["Min"] + temp_df["Max"]) / 2

temp_daily = temp_df.groupby("date")["temp_avg"].mean().reset_index()
merged = pd.merge(daily, temp_daily, on="date", how="inner")

temp_voltage_data = []
for _, row in merged.iterrows():
    temp_voltage_data.append(
        {"temp": round(row["temp_avg"], 1), "voltage": round(row["avg"] * 1000, 1)}
    )

# Generate HTML
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voltage Trend - LiFePO4 Battery Study</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f6f8fa;
        }
        h1, h2 { color: #24292e; }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .stat-label { font-size: 0.85em; color: #586069; margin-bottom: 5px; }
        .stat-value { font-size: 1.5em; font-weight: 600; color: #24292e; }
        .stat-unit { font-size: 0.9em; color: #586069; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #0366d6; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
        .phase-label { padding: 4px 8px; border-radius: 3px; font-size: 0.85em; font-weight: 500; display: inline-block; margin: 0 5px; }
        .phase-stasis { background-color: #dbedff; color: #0366d6; }
        .phase-charge { background-color: #fff3cd; color: #856404; }
        .phase-current { background-color: #dcffe4; color: #28a745; }
        .annotations { background: #fffbdd; border-left: 4px solid #ffd33d; padding: 15px; margin: 20px 0; border-radius: 3px; }
        canvas { max-height: 500px; }
    </style>
</head>
<body>
    <a href="https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks" class="back-link">Back to Repository</a>

    <h1>130-Day Voltage Trend Analysis</h1>
    <p>Interactive visualization of continuous bus voltage monitoring (Oct 29, 2025 - Mar 5, 2026)</p>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Duration</div>
            <div class="stat-value">130<span class="stat-unit"> days</span></div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Stasis Drift (92d)</div>
            <div class="stat-value">-0.58<span class="stat-unit"> mV/day</span></div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Current Drift</div>
            <div class="stat-value">-4.75<span class="stat-unit"> mV/day</span></div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Parasitic Draw</div>
            <div class="stat-value">12.5<span class="stat-unit"> mA</span></div>
        </div>
    </div>

    <div class="annotations">
        <strong>Study Phases:</strong>
        <span class="phase-label phase-stasis">Pre-charge Stasis (Nov 22 - Feb 21)</span>
        <span class="phase-label phase-charge">Charge Event (Feb 22)</span>
        <span class="phase-label phase-current">Post-charge Settling (Feb 22 - present)</span>
        <br><br>
        <strong>Note:</strong> Voltage measurements represent bus-level potential (single Shelly Plus Uni sensor).
        High spikes indicate charge events (Nov 1, Nov 4, Feb 22).
    </div>

    <div class="chart-container">
        <h2>Bus Voltage Over Time</h2>
        <canvas id="voltageChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Temperature-Voltage Correlation (TEMP_DAYS days)</h2>
        <canvas id="tempChart"></canvas>
    </div>

    <script>
        const voltageData = VOLTAGE_DATA_PLACEHOLDER;
        const tempVoltageData = TEMP_DATA_PLACEHOLDER;

        // Chart 1: Main voltage trend
        const ctx1 = document.getElementById('voltageChart').getContext('2d');
        new Chart(ctx1, {
            type: 'line',
            data: {
                labels: voltageData.map(d => d.date),
                datasets: [
                    {
                        label: 'Daily Mean (mV)',
                        data: voltageData.map(d => d.voltage),
                        borderColor: '#0366d6',
                        backgroundColor: 'rgba(3, 102, 214, 0.1)',
                        tension: 0.1,
                        pointRadius: 1,
                        borderWidth: 2,
                        fill: false
                    },
                    {
                        label: 'Daily Max',
                        data: voltageData.map(d => d.vmax),
                        borderColor: 'rgba(203, 36, 49, 0.4)',
                        backgroundColor: 'transparent',
                        tension: 0.1,
                        pointRadius: 0,
                        borderWidth: 1,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Daily Min',
                        data: voltageData.map(d => d.vmin),
                        borderColor: 'rgba(40, 167, 69, 0.4)',
                        backgroundColor: 'transparent',
                        tension: 0.1,
                        pointRadius: 0,
                        borderWidth: 1,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + (context.parsed.y / 1000).toFixed(3) + ' V';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'week', displayFormats: { week: 'MMM d' } },
                        title: { display: true, text: 'Date (2025-2026)' }
                    },
                    y: {
                        title: { display: true, text: 'Voltage (mV)' },
                        min: 12500,
                        max: 15000,
                        ticks: { callback: function(value) { return value.toFixed(0); } }
                    }
                }
            }
        });

        // Chart 2: Temperature correlation
        const ctx2 = document.getElementById('tempChart').getContext('2d');
        new Chart(ctx2, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Voltage vs Temperature',
                    data: tempVoltageData.map(d => ({x: d.temp, y: d.voltage})),
                    backgroundColor: 'rgba(40, 167, 69, 0.6)',
                    borderColor: '#28a745',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.x.toFixed(1) + ' F -> ' + (context.parsed.y / 1000).toFixed(3) + ' V';
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Temperature (F)' }, min: 50, max: 60 },
                    y: { title: { display: true, text: 'Voltage (mV)' }, min: 13200, max: 13500 }
                }
            }
        });
    </script>

    <div style="margin-top: 40px; padding: 20px; background: #f6f8fa; border-radius: 6px;">
        <h3>Data Notes</h3>
        <ul>
            <li><strong>Voltage values</strong> are bus-level measurements from a Shelly Plus Uni voltmeter</li>
            <li><strong>Charge events</strong> visible as voltage spikes: Nov 1, Nov 4, 2025 and Feb 22, 2026</li>
            <li><strong>Temperature data</strong> covers TEMP_DAYS days (Jan 1 - Mar 6, 2026)</li>
            <li><strong>Current status:</strong> Approaching stasis after Feb 22 charge (-4.75 mV/day drift)</li>
        </ul>
        <p><em>Last updated: March 6, 2026</em></p>
    </div>

    <a href="https://github.com/wkcollis1-eng/Lifepo4-Battery-Banks" class="back-link">Back to Repository</a>
</body>
</html>
"""

# Replace placeholders
html_content = html_template.replace(
    "VOLTAGE_DATA_PLACEHOLDER", json.dumps(voltage_data)
)
html_content = html_content.replace(
    "TEMP_DATA_PLACEHOLDER", json.dumps(temp_voltage_data)
)
html_content = html_content.replace("TEMP_DAYS", str(len(temp_voltage_data)))

# Write the file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated voltage_chart.html with actual data")
print(f"- {len(voltage_data)} days of voltage data")
print(f"- {len(temp_voltage_data)} days of temperature-voltage correlation data")
