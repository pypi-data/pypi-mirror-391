import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Temperature ranges for two cities
city1_ranges = {
    "January": (10, 15),
    "February": (12, 20),
    "March": (18, 25),
    "April": (24, 30),
    "May": (27, 32),
    "June": (25, 27),
    "July": (23, 26),
    "August": (23, 24),
    "September": (20, 22),
    "October": (20, 21),
    "November": (14, 20),
    "December": (10, 17)
}

city2_ranges = {
    "January": (2, 7),
    "February": (3, 9),
    "March": (8, 15),
    "April": (15, 20),
    "May": (20, 25),
    "June": (24, 30),
    "July": (28, 35),
    "August": (27, 34),
    "September": (22, 28),
    "October": (16, 22),
    "November": (10, 16),
    "December": (5, 10)
}

# Common setup
months = list(city1_ranges.keys())
month_indices = np.arange(len(months))

def generate_avg_temps(ranges):
    averages = []
    for month in months:
        low, high = ranges[month]
        temps = np.random.uniform(low, high, 10)
        averages.append(np.mean(temps))
    return averages

# Generate average temps for both cities
city1_avg = generate_avg_temps(city1_ranges)
city2_avg = generate_avg_temps(city2_ranges)

# Smooth the curves
x_smooth = np.linspace(month_indices.min(), month_indices.max(), 300)
city1_spline = make_interp_spline(month_indices, city1_avg, k=3)(x_smooth)
city2_spline = make_interp_spline(month_indices, city2_avg, k=3)(x_smooth)

# Find warmest and coldest for City 1 only
max_temp = max(city1_avg)
min_temp = min(city1_avg)
max_index = city1_avg.index(max_temp)
min_index = city1_avg.index(min_temp)

# Plotting
plt.figure(figsize=(14, 6))

# Plot smooth lines
plt.plot(x_smooth, city1_spline, color='crimson', linewidth=2.5, label='City 1 Avg')
plt.plot(x_smooth, city2_spline, color='royalblue', linewidth=2.5, label='City 2 Avg')

# Scatter actual monthly averages
plt.scatter(month_indices, city1_avg, color='black', zorder=5, label='City 1 Monthly Avg')
plt.scatter(month_indices, city2_avg, color='gray', zorder=5, label='City 2 Monthly Avg')

# Highlight City 1 warmest and coldest
plt.scatter(month_indices[max_index], max_temp, color='red', s=100, zorder=6, label='City 1 Warmest')
plt.scatter(month_indices[min_index], min_temp, color='blue', s=100, zorder=6, label='City 1 Coldest')

# Add text labels
plt.text(month_indices[max_index], max_temp + 0.8,
         f'{months[max_index]}\n{max_temp:.1f}°C',
         ha='center', color='red', fontsize=9)

plt.text(month_indices[min_index], min_temp - 1.2,
         f'{months[min_index]}\n{min_temp:.1f}°C',
         ha='center', color='blue', fontsize=9)

# X-axis tweaks
abbrev_months = [m[:3] for m in months]
plt.xticks(month_indices, abbrev_months, rotation=0)

# Labels, grid, legend
plt.title('Smooth Average Monthly Temperature Comparison')
plt.xlabel('Month')
plt.ylabel('Average Temperature (°C)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()


import matplotlib.pyplot as plt
import numpy as np

# Example data (replace with actual values)
channels = ['Social Media', 'Google Ads', 'Email', 'Referrals']

# Sign-ups for previous and current quarter
sign_ups_prev = [280, 390, 240, 200]  # Previous quarter
sign_ups_curr = [320, 450, 210, 180]  # Current quarter

# Sort channels by current quarter performance
sorted_data = sorted(zip(sign_ups_curr, sign_ups_prev, channels), reverse=True)
sign_ups_curr_sorted, sign_ups_prev_sorted, channels_sorted = zip(*sorted_data)

# Bar settings
x = np.arange(len(channels_sorted))  # the label locations
width = 0.35  # the width of the bars

# Create the plot
plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width/2, sign_ups_prev_sorted, width, label='Previous Quarter', color='#ff7f0e')
bars2 = plt.bar(x + width/2, sign_ups_curr_sorted, width, label='Current Quarter', color='#1f77b4')

# Title and labels
plt.title('New Customer Sign-Ups by Advertising Channel (Quarterly Comparison)', fontsize=14)
plt.xlabel('Advertising Channel', fontsize=12)
plt.ylabel('Number of Sign-Ups', fontsize=12)
plt.xticks(x, channels_sorted)

# Add data labels
for bars in [bars1, bars2]:
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 10, str(yval),
                 ha='center', va='bottom', fontsize=9)

# Add legend and layout tweaks
plt.legend()
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt

# Example data
departments = ['R&D', 'Marketing', 'Sales', 'Operations', 'HR']
budget = [25, 15, 20, 30, 10]  # Budget in millions

# Emphasize only the R&D slice
explode = [0.1 if dept == 'R&D' else 0 for dept in departments]

# Create the pie chart
plt.figure(figsize=(8, 8))
colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854']

plt.pie(
    budget,
    labels=departments,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    explode=explode,
    shadow=True
)

plt.title('Annual Budget Allocation by Department', fontsize=14)
plt.tight_layout()
plt.show()

#4. Scatter plot
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# Seed for reproducibility
np.random.seed(42)

fertilizer_kg = np.linspace(10, 100, 30)
crop_yield_bu = 0.5 * fertilizer_kg + np.random.normal(0, 8, size=fertilizer_kg.size)
soil_types = np.random.choice(['Clay', 'Sandy', 'Loamy'], size=fertilizer_kg.size)

soil_color_map = {
    'Clay': '#1f77b4',   
    'Sandy': '#ff7f0e',  
    'Loamy': '#2ca02c'   
}
colors = [soil_color_map[soil] for soil in soil_types]

plt.figure(figsize=(9, 6))
plt.scatter(fertilizer_kg, crop_yield_bu, c=colors, alpha=0.8, edgecolor='k', s=100)

coefficients = np.polyfit(fertilizer_kg, crop_yield_bu, deg=1)
poly_fn = np.poly1d(coefficients)

x_vals = np.linspace(fertilizer_kg.min(), fertilizer_kg.max(), 100)
plt.plot(x_vals, poly_fn(x_vals), color='black', linestyle='--', linewidth=2, label='Trendline')

plt.title('Fertilizer Usage vs. Crop Yield by Soil Type', fontsize=16)
plt.xlabel('Fertilizer Used (kg)', fontsize=14)
plt.ylabel('Crop Yield (bushels)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)

legend_elements = [Line2D([0], [0], marker='o', color='w', label=soil,
                          markerfacecolor=color, markeredgecolor='k', markersize=12)
                   for soil, color in soil_color_map.items()]
legend_elements.append(Line2D([0], [0], color='black', lw=2, linestyle='--', label='Trendline'))
plt.legend(handles=legend_elements, title='Soil Type', fontsize=12, title_fontsize=13)

plt.tight_layout()
plt.show()

