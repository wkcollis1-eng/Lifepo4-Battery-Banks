#!/usr/bin/env python3
"""
Detailed Visualizations and Deep Dive Analysis
LiFePO4 Battery System - January 8, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set up matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# ============================================================================
# LOAD DATA
# ============================================================================

# Load hourly aggregated data
hourly_df = pd.read_csv('/mnt/user-data/uploads/combined_output.csv')
hourly_df['Datetime'] = pd.to_datetime(hourly_df['Date'] + ' ' + hourly_df['Time'], 
                                        format='%d/%m/%Y %H:%M')
hourly_df = hourly_df.sort_values('Datetime')
hourly_df['Midpoint'] = (hourly_df['Min'] + hourly_df['Max']) / 2
hourly_df['Spread'] = hourly_df['Max'] - hourly_df['Min']

# Load high-frequency data
hf_df = pd.read_csv('/mnt/user-data/uploads/history.csv')
hf_df = hf_df[pd.to_numeric(hf_df['state'], errors='coerce').notna()]
hf_df['Datetime'] = pd.to_datetime(hf_df['last_changed'])
hf_df['voltage'] = hf_df['state'].astype(float)
hf_df = hf_df.sort_values('Datetime')

# Load temperature data
temp_df = pd.read_csv('/mnt/user-data/uploads/Combined_Temperature_Data.csv')
temp_df['Datetime'] = pd.to_datetime(temp_df['Date'] + ' ' + temp_df['Time'], 
                                      format='%d/%m/%Y %H:%M')
temp_df['Temp_Midpoint'] = (temp_df['Min'] + temp_df['Max']) / 2
temp_df = temp_df.sort_values('Datetime')

# Load humidity data
humid_df = pd.read_csv('/mnt/user-data/uploads/Combined_Humidity_Data.csv')
humid_df['Datetime'] = pd.to_datetime(humid_df['Date'] + ' ' + humid_df['Time'], 
                                       format='%d/%m/%Y %H:%M')
humid_df = humid_df.sort_values('Datetime')

# ============================================================================
# FIGURE 1: Complete Voltage Timeline
# ============================================================================

fig1, axes = plt.subplots(3, 1, figsize=(16, 12))

# Plot 1a: Full voltage history with Min/Max bands
ax1 = axes[0]
ax1.fill_between(hourly_df['Datetime'], hourly_df['Min'], hourly_df['Max'], 
                  alpha=0.3, color='blue', label='Min-Max Range')
ax1.plot(hourly_df['Datetime'], hourly_df['Midpoint'], 'b-', linewidth=0.8, 
         label='Midpoint Voltage')

# Add key events
ax1.axvline(pd.Timestamp('2025-11-02'), color='red', linestyle='--', alpha=0.7, label='Discharge Test')
ax1.axvline(pd.Timestamp('2025-11-04'), color='green', linestyle='--', alpha=0.7, label='Recharge Complete')
ax1.axvline(pd.Timestamp('2025-12-19'), color='orange', linestyle='--', alpha=0.7, label='Dec 19 Anomaly')
ax1.axvline(pd.Timestamp('2025-12-23 15:40'), color='purple', linestyle='--', alpha=0.7, label='Eco Mode')

ax1.set_ylabel('Voltage (V)')
ax1.set_title('Complete Voltage History: Oct 29, 2025 - Jan 7, 2026')
ax1.legend(loc='upper right', fontsize=8)
ax1.set_ylim(12.5, 14.6)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 1b: Stasis period zoom (Nov 8 - Jan 7)
ax2 = axes[1]
stasis = hourly_df[hourly_df['Datetime'] >= '2025-11-08']
ax2.fill_between(stasis['Datetime'], stasis['Min'], stasis['Max'], 
                  alpha=0.3, color='blue')
ax2.plot(stasis['Datetime'], stasis['Midpoint'], 'b-', linewidth=0.8)

# Add eco mode line
ax2.axvline(pd.Timestamp('2025-12-23 15:40'), color='purple', linestyle='--', 
            alpha=0.7, label='Eco Mode Enabled')
ax2.axhline(13.33, color='gray', linestyle=':', alpha=0.7, label='Reported 100% SOC (13.33V)')

ax2.set_ylabel('Voltage (V)')
ax2.set_title('Stasis Period: Nov 8, 2025 - Jan 7, 2026 (Settlement + Winter Drift)')
ax2.legend(loc='upper right', fontsize=8)
ax2.set_ylim(13.15, 13.45)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Plot 1c: Post-Eco detailed view
ax3 = axes[2]
post_eco = hourly_df[hourly_df['Datetime'] >= '2025-12-23']
ax3.fill_between(post_eco['Datetime'], post_eco['Min'], post_eco['Max'], 
                  alpha=0.3, color='blue')
ax3.plot(post_eco['Datetime'], post_eco['Midpoint'], 'b-', linewidth=1.0)
ax3.scatter(post_eco['Datetime'], post_eco['Min'], s=5, color='red', alpha=0.5, label='Min')
ax3.scatter(post_eco['Datetime'], post_eco['Max'], s=5, color='green', alpha=0.5, label='Max')

ax3.set_xlabel('Date')
ax3.set_ylabel('Voltage (V)')
ax3.set_title('Post-Eco Mode Detail: Dec 23, 2025 - Jan 7, 2026')
ax3.legend(loc='upper right', fontsize=8)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax3.xaxis.set_major_locator(mdates.DayLocator(interval=2))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/fig1_voltage_timeline.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# FIGURE 2: Spread Analysis (Cell Divergence Investigation)
# ============================================================================

fig2, axes = plt.subplots(2, 2, figsize=(16, 10))

# Plot 2a: Spread over time
ax1 = axes[0, 0]
ax1.plot(hourly_df['Datetime'], hourly_df['Spread']*1000, 'b-', alpha=0.5, linewidth=0.5)
# Rolling average
hourly_df['Spread_MA'] = hourly_df['Spread'].rolling(24).mean()
ax1.plot(hourly_df['Datetime'], hourly_df['Spread_MA']*1000, 'r-', linewidth=2, label='24h Moving Avg')
ax1.axhline(50, color='orange', linestyle='--', label='50mV Reference')
ax1.set_ylabel('Voltage Spread (mV)')
ax1.set_title('Min-Max Spread Over Time (Cell Balance Indicator)')
ax1.legend()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 2b: Spread histogram by month
ax2 = axes[0, 1]
hourly_df['Month'] = hourly_df['Datetime'].dt.to_period('M')
months = hourly_df['Month'].unique()
colors = plt.cm.viridis(np.linspace(0, 1, len(months)))
for i, month in enumerate(months):
    data = hourly_df[hourly_df['Month'] == month]['Spread'] * 1000
    ax2.hist(data, bins=30, alpha=0.5, color=colors[i], label=str(month))
ax2.set_xlabel('Spread (mV)')
ax2.set_ylabel('Frequency')
ax2.set_title('Spread Distribution by Month')
ax2.legend(fontsize=8)

# Plot 2c: Spread vs Voltage
ax3 = axes[1, 0]
# Color by time
scatter = ax3.scatter(hourly_df['Midpoint'], hourly_df['Spread']*1000, 
                      c=hourly_df['Datetime'].astype(np.int64), 
                      cmap='viridis', alpha=0.5, s=10)
ax3.set_xlabel('Midpoint Voltage (V)')
ax3.set_ylabel('Spread (mV)')
ax3.set_title('Spread vs Voltage Level (colored by time)')
cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('Time')

# Plot 2d: Daily spread statistics
ax4 = axes[1, 1]
hourly_df['Date_only'] = hourly_df['Datetime'].dt.date
daily_spread = hourly_df.groupby('Date_only')['Spread'].agg(['mean', 'std', 'max']).reset_index()
daily_spread['Date_only'] = pd.to_datetime(daily_spread['Date_only'])
ax4.plot(daily_spread['Date_only'], daily_spread['mean']*1000, 'b-', label='Mean')
ax4.fill_between(daily_spread['Date_only'], 
                 (daily_spread['mean'] - daily_spread['std'])*1000,
                 (daily_spread['mean'] + daily_spread['std'])*1000, 
                 alpha=0.3, label='±1 Std Dev')
ax4.plot(daily_spread['Date_only'], daily_spread['max']*1000, 'r--', alpha=0.5, label='Max')
ax4.set_xlabel('Date')
ax4.set_ylabel('Spread (mV)')
ax4.set_title('Daily Spread Statistics')
ax4.legend()
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/fig2_spread_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# FIGURE 3: High-Frequency Analysis with MA-60s
# ============================================================================

fig3, axes = plt.subplots(2, 2, figsize=(16, 10))

# Filter to raw high-frequency data only
hf_raw = hf_df[hf_df['voltage'].apply(lambda x: len(str(x).split('.')[-1]) <= 2)].copy()

# Calculate 60-second MA
hf_raw['minute_bucket'] = hf_raw['Datetime'].dt.floor('60s')
ma60 = hf_raw.groupby('minute_bucket').agg({
    'voltage': ['mean', 'std', 'min', 'max', 'count']
}).reset_index()
ma60.columns = ['Datetime', 'MA60_Mean', 'MA60_Std', 'MA60_Min', 'MA60_Max', 'Sample_Count']
ma60 = ma60[ma60['Sample_Count'] > 3]

# Plot 3a: MA-60 over time
ax1 = axes[0, 0]
ax1.plot(ma60['Datetime'], ma60['MA60_Mean'], 'b-', linewidth=0.5, alpha=0.7)
# Add daily average overlay
ma60['Date'] = ma60['Datetime'].dt.date
daily_ma60 = ma60.groupby('Date')['MA60_Mean'].mean().reset_index()
daily_ma60['Date'] = pd.to_datetime(daily_ma60['Date'])
ax1.plot(daily_ma60['Date'], daily_ma60['MA60_Mean'], 'r-', linewidth=2, label='Daily Average')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('60-Second Moving Average (Dec 29, 2025 - Jan 8, 2026)')
ax1.legend()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 3b: Within-bucket noise (std dev)
ax2 = axes[0, 1]
ax2.scatter(ma60['Datetime'], ma60['MA60_Std']*1000, s=1, alpha=0.3)
ax2.axhline(ma60['MA60_Std'].mean()*1000, color='red', linestyle='--', 
            label=f'Mean: {ma60["MA60_Std"].mean()*1000:.1f}mV')
ax2.set_ylabel('Std Dev (mV)')
ax2.set_title('Voltage Noise Within 60s Windows')
ax2.legend()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Plot 3c: Raw voltage distribution
ax3 = axes[1, 0]
voltage_counts = hf_raw['voltage'].value_counts().sort_index()
ax3.bar(voltage_counts.index, voltage_counts.values, width=0.008, color='blue', alpha=0.7)
ax3.set_xlabel('Voltage (V)')
ax3.set_ylabel('Count')
ax3.set_title('Raw Voltage Value Distribution (10mV ADC Resolution)')
ax3.set_xlim(13.18, 13.30)

# Plot 3d: Sample rate over time
ax4 = axes[1, 1]
ax4.scatter(ma60['Datetime'], ma60['Sample_Count'], s=2, alpha=0.3)
ax4.axhline(ma60['Sample_Count'].mean(), color='red', linestyle='--',
            label=f'Mean: {ma60["Sample_Count"].mean():.1f} samples/min')
ax4.set_ylabel('Samples per 60s')
ax4.set_title('Sampling Rate Over Time')
ax4.legend()
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/fig3_high_freq_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# FIGURE 4: Temperature-Voltage Correlation
# ============================================================================

fig4, axes = plt.subplots(2, 2, figsize=(16, 10))

# Merge data
merged = pd.merge_asof(
    hourly_df.sort_values('Datetime'),
    temp_df[['Datetime', 'Temp_Midpoint']].sort_values('Datetime'),
    on='Datetime',
    tolerance=pd.Timedelta('1H')
)
merged = merged.dropna(subset=['Temp_Midpoint'])

# Also merge humidity
merged = pd.merge_asof(
    merged.sort_values('Datetime'),
    humid_df[['Datetime', 'Humidity']].sort_values('Datetime'),
    on='Datetime',
    tolerance=pd.Timedelta('1H')
)

# Plot 4a: Temperature and Voltage over time (dual axis)
ax1 = axes[0, 0]
ax1_twin = ax1.twinx()
ax1.plot(merged['Datetime'], merged['Midpoint'], 'b-', linewidth=1, label='Voltage')
ax1_twin.plot(merged['Datetime'], merged['Temp_Midpoint'], 'r-', linewidth=1, label='Temperature')
ax1.set_ylabel('Voltage (V)', color='blue')
ax1_twin.set_ylabel('Temperature (°F)', color='red')
ax1.set_title('Voltage and Temperature Over Time')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 4b: Scatter plot with regression
ax2 = axes[0, 1]
slope, intercept, r_value, p_value, std_err = stats.linregress(
    merged['Temp_Midpoint'], merged['Midpoint']
)
ax2.scatter(merged['Temp_Midpoint'], merged['Midpoint'], alpha=0.5, s=20)
x_line = np.array([merged['Temp_Midpoint'].min(), merged['Temp_Midpoint'].max()])
y_line = slope * x_line + intercept
ax2.plot(x_line, y_line, 'r-', linewidth=2, 
         label=f'R²={r_value**2:.4f}\nSlope={slope*1000:.2f}mV/°F')
ax2.set_xlabel('Temperature (°F)')
ax2.set_ylabel('Voltage (V)')
ax2.set_title('Voltage vs Temperature Scatter')
ax2.legend()

# Plot 4c: Humidity effect
ax3 = axes[1, 0]
if 'Humidity' in merged.columns and merged['Humidity'].notna().sum() > 0:
    h_slope, h_intercept, h_r, h_p, h_se = stats.linregress(
        merged['Humidity'].dropna(), 
        merged.loc[merged['Humidity'].notna(), 'Midpoint']
    )
    ax3.scatter(merged['Humidity'], merged['Midpoint'], alpha=0.5, s=20)
    ax3.set_xlabel('Humidity (%)')
    ax3.set_ylabel('Voltage (V)')
    ax3.set_title(f'Voltage vs Humidity (R²={h_r**2:.4f})')
else:
    ax3.text(0.5, 0.5, 'No humidity data available', ha='center', va='center')

# Plot 4d: Diurnal pattern
ax4 = axes[1, 1]
merged['Hour'] = merged['Datetime'].dt.hour
hourly_pattern = merged.groupby('Hour').agg({
    'Midpoint': ['mean', 'std'],
    'Temp_Midpoint': 'mean'
}).reset_index()
hourly_pattern.columns = ['Hour', 'V_Mean', 'V_Std', 'T_Mean']

ax4_twin = ax4.twinx()
ax4.errorbar(hourly_pattern['Hour'], hourly_pattern['V_Mean'], 
             yerr=hourly_pattern['V_Std'], fmt='b-o', capsize=3, label='Voltage')
ax4_twin.plot(hourly_pattern['Hour'], hourly_pattern['T_Mean'], 'r--s', label='Temperature')
ax4.set_xlabel('Hour of Day')
ax4.set_ylabel('Voltage (V)', color='blue')
ax4_twin.set_ylabel('Temperature (°F)', color='red')
ax4.set_title('Diurnal Pattern (Dec 29 - Jan 7)')
ax4.set_xticks(range(0, 24, 3))

plt.tight_layout()
plt.savefig('/home/claude/fig4_temp_correlation.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# FIGURE 5: Drift Rate Analysis
# ============================================================================

fig5, axes = plt.subplots(2, 2, figsize=(16, 10))

# Calculate rolling drift rate
hourly_df_sorted = hourly_df.sort_values('Datetime').copy()
# 7-day rolling regression for drift rate
window_size = 24 * 7  # 7 days in hours
drift_rates = []
drift_dates = []

for i in range(window_size, len(hourly_df_sorted)):
    window = hourly_df_sorted.iloc[i-window_size:i]
    x = np.arange(len(window))
    y = window['Midpoint'].values
    if len(x) > 10:
        slope, _, _, _, _ = stats.linregress(x, y)
        drift_rates.append(slope * 24 * 1000)  # mV per day
        drift_dates.append(window['Datetime'].iloc[-1])

# Plot 5a: Rolling drift rate
ax1 = axes[0, 0]
ax1.plot(drift_dates, drift_rates, 'b-', linewidth=1)
ax1.axhline(0, color='gray', linestyle='--')
ax1.set_ylabel('Drift Rate (mV/day)')
ax1.set_title('7-Day Rolling Drift Rate')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 5b: Cumulative drift from Nov 22
ax2 = axes[0, 1]
stasis_start = hourly_df_sorted[hourly_df_sorted['Datetime'] >= '2025-11-22'].copy()
if len(stasis_start) > 0:
    baseline = stasis_start.iloc[0]['Midpoint']
    stasis_start['Cumulative_Drift'] = (stasis_start['Midpoint'] - baseline) * 1000
    ax2.plot(stasis_start['Datetime'], stasis_start['Cumulative_Drift'], 'b-', linewidth=0.5)
    # Add 24h MA
    stasis_start['Drift_MA'] = stasis_start['Cumulative_Drift'].rolling(24).mean()
    ax2.plot(stasis_start['Datetime'], stasis_start['Drift_MA'], 'r-', linewidth=2, label='24h MA')
    ax2.axhline(0, color='gray', linestyle='--')
    ax2.axhline(-90, color='orange', linestyle='--', label='Reported 90mV drift')
    ax2.set_ylabel('Cumulative Drift (mV)')
    ax2.set_title('Cumulative Voltage Drift from Nov 22')
    ax2.legend()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Plot 5c: Weekly drift comparison
ax3 = axes[1, 0]
weekly_stats = []
start_date = pd.Timestamp('2025-11-22')
while start_date < hourly_df_sorted['Datetime'].max():
    end_date = start_date + pd.Timedelta(days=7)
    week_data = hourly_df_sorted[(hourly_df_sorted['Datetime'] >= start_date) & 
                                  (hourly_df_sorted['Datetime'] < end_date)]
    if len(week_data) > 48:
        x = np.arange(len(week_data))
        slope, _, _, _, _ = stats.linregress(x, week_data['Midpoint'].values)
        weekly_stats.append({
            'Week': start_date.strftime('%b %d'),
            'Drift': slope * 24 * 7 * 1000,  # Total mV over week
            'Mean': week_data['Midpoint'].mean()
        })
    start_date = end_date

if weekly_stats:
    week_df = pd.DataFrame(weekly_stats)
    bars = ax3.bar(range(len(week_df)), week_df['Drift'], color='blue', alpha=0.7)
    ax3.set_xticks(range(len(week_df)))
    ax3.set_xticklabels(week_df['Week'], rotation=45)
    ax3.set_ylabel('Weekly Drift (mV)')
    ax3.set_title('Weekly Drift Rate Comparison')
    ax3.axhline(0, color='gray', linestyle='--')

# Plot 5d: Voltage level over time with phases
ax4 = axes[1, 1]
ax4.plot(hourly_df_sorted['Datetime'], hourly_df_sorted['Midpoint'], 'b-', linewidth=0.5, alpha=0.5)
# Add phase annotations
phases = [
    ('2025-10-29', '2025-11-02', 'Pre-Test', 'lightblue'),
    ('2025-11-02', '2025-11-04', 'Test+Recharge', 'yellow'),
    ('2025-11-04', '2025-11-22', 'Settlement', 'lightgreen'),
    ('2025-11-22', '2025-12-23', 'Winter Drift', 'lightyellow'),
    ('2025-12-23', '2026-01-08', 'Post-Eco', 'lavender')
]
for start, end, label, color in phases:
    ax4.axvspan(pd.Timestamp(start), pd.Timestamp(end), alpha=0.3, color=color, label=label)
ax4.set_ylabel('Voltage (V)')
ax4.set_title('Voltage Phases')
ax4.legend(loc='upper right', fontsize=8)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/fig5_drift_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# FIGURE 6: Anomaly Analysis
# ============================================================================

fig6, axes = plt.subplots(2, 2, figsize=(16, 10))

# Plot 6a: Dec 19 anomaly detail
ax1 = axes[0, 0]
dec_window = hourly_df[(hourly_df['Datetime'] >= '2025-12-17') & 
                        (hourly_df['Datetime'] <= '2025-12-21')]
ax1.fill_between(dec_window['Datetime'], dec_window['Min'], dec_window['Max'], 
                  alpha=0.3, color='blue')
ax1.plot(dec_window['Datetime'], dec_window['Min'], 'r-', label='Min', linewidth=1.5)
ax1.plot(dec_window['Datetime'], dec_window['Max'], 'g-', label='Max', linewidth=1.5)
ax1.axvline(pd.Timestamp('2025-12-19'), color='orange', linestyle='--', label='Dec 19')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('Dec 19 Anomaly Detail (EMI Event)')
ax1.legend()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Plot 6b: Eco mode transition detail
ax2 = axes[0, 1]
eco_window = hourly_df[(hourly_df['Datetime'] >= '2025-12-22') & 
                        (hourly_df['Datetime'] <= '2025-12-25')]
ax2.plot(eco_window['Datetime'], eco_window['Min'], 'r-', label='Min', linewidth=1.5)
ax2.plot(eco_window['Datetime'], eco_window['Max'], 'g-', label='Max', linewidth=1.5)
ax2.axvline(pd.Timestamp('2025-12-23 15:40'), color='purple', linestyle='--', label='Eco Mode Enabled')
ax2.set_ylabel('Voltage (V)')
ax2.set_title('Eco Mode Transition Detail')
ax2.legend()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Plot 6c: Spread anomalies
ax3 = axes[1, 0]
stasis = hourly_df[hourly_df['Datetime'] >= '2025-11-08'].copy()
mean_spread = stasis['Spread'].mean()
std_spread = stasis['Spread'].std()
anomaly_threshold = mean_spread + 2 * std_spread
ax3.plot(stasis['Datetime'], stasis['Spread']*1000, 'b-', alpha=0.5, linewidth=0.5)
ax3.axhline(mean_spread*1000, color='green', linestyle='-', label=f'Mean: {mean_spread*1000:.1f}mV')
ax3.axhline(anomaly_threshold*1000, color='red', linestyle='--', label=f'2σ: {anomaly_threshold*1000:.1f}mV')
anomalies = stasis[stasis['Spread'] > anomaly_threshold]
if len(anomalies) > 0:
    ax3.scatter(anomalies['Datetime'], anomalies['Spread']*1000, color='red', s=20, zorder=5, label='Anomalies')
ax3.set_ylabel('Spread (mV)')
ax3.set_title(f'Spread Anomalies (n={len(anomalies)})')
ax3.legend()
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

# Plot 6d: Time series of anomaly events
ax4 = axes[1, 1]
# Find all hours where Min dropped significantly
stasis['Min_Change'] = stasis['Min'].diff()
significant_drops = stasis[stasis['Min_Change'] < -0.02]  # >20mV drop
ax4.scatter(significant_drops['Datetime'], significant_drops['Min_Change']*1000, 
            s=30, color='red', alpha=0.7)
ax4.axhline(0, color='gray', linestyle='--')
ax4.axhline(-20, color='orange', linestyle='--', label='-20mV threshold')
ax4.set_ylabel('Hour-to-Hour Min Change (mV)')
ax4.set_title(f'Significant Min Voltage Drops (n={len(significant_drops)})')
ax4.legend()
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/fig6_anomaly_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print("✅ All figures generated successfully!")
print("\nFigure files created:")
print("  - fig1_voltage_timeline.png")
print("  - fig2_spread_analysis.png")
print("  - fig3_high_freq_analysis.png")
print("  - fig4_temp_correlation.png")
print("  - fig5_drift_analysis.png")
print("  - fig6_anomaly_analysis.png")
