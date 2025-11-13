import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

data = np.random.normal(loc=0, scale=1, size=1000)

sns.set(style="whitegrid")
sns.histplot(data, kde=True, bins=30, color='skyblue')

plt.title('Sample Distribution Plot')
plt.xlabel('Value')
plt.ylabel('Frequency')

plt.show()

import seaborn as sns

# Load dataset
mpg = sns.load_dataset("mpg").dropna()  # Remove missing data

# Set theme
sns.set_theme(style="whitegrid", context="notebook")

# Create scatter plot
sns.scatterplot(
    data=mpg,
    x="horsepower",
    y="mpg",
    hue="origin",
    style="cylinders",
    size="weight",
    palette="Dark2",
    sizes=(30, 300),
    alpha=0.7,
    edgecolor="black"
).set(
    title="Fuel Efficiency vs Horsepower",
    xlabel="Horsepower",
    ylabel="Miles per Gallon (MPG)"
)

sns.despine(trim=True)

import seaborn as sns

# Load and clean dataset
mpg = sns.load_dataset("mpg").dropna()

# Set theme
sns.set_theme(style="white", context="notebook")

# Hexbin-style density plot
sns.histplot(
    data=mpg,
    x="horsepower",
    y="mpg",
    bins=30,
    cbar=True,         # Colorbar to show density
    pmax=0.9,          # Clip extreme outliers
    cmap="viridis",    # Good perceptual color map
    binrange=[[40, 240], [5, 50]],  # Focused plot range
    kde=False,
    stat="count",
    discrete=False
).set(
    title="Hexbin-style Plot: Horsepower vs MPG",
    xlabel="Horsepower",
    ylabel="Miles per Gallon (MPG)"
)

sns.despine()

import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Generate a reasonably large dataset
n_customers = 2000

# Create columns
customer_data = pd.DataFrame({
    "CustomerID": range(1, n_customers + 1),
    "Age": np.random.randint(18, 70, size=n_customers),
    "Gender": np.random.choice(["Male", "Female", "Other"], size=n_customers, p=[0.45, 0.45, 0.1]),
    "Location": np.random.choice(["North", "South", "East", "West"], size=n_customers),
    "TotalPurchases": np.random.poisson(lam=20, size=n_customers),
    "AverageOrderValue": np.round(np.random.normal(loc=75, scale=20, size=n_customers), 2),
    "LastPurchaseDaysAgo": np.random.randint(0, 365, size=n_customers),
    "PreferredCategory": np.random.choice(
        ["Apparel", "Footwear", "Accessories", "Electronics"],
        size=n_customers,
        p=[0.4, 0.3, 0.2, 0.1]
    ),
    "SubscriptionStatus": np.random.choice(["Yes", "No"], size=n_customers, p=[0.6, 0.4]),
    "LoyaltyProgramMember": np.random.choice(["Yes", "No"], size=n_customers, p=[0.5, 0.5])
})

# Display first few rows
print(customer_data.head())

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

sns.histplot(
    customer_data['Age'],
    bins=30,
    kde=True,
    color=sns.color_palette("mako")[4],  #
    linewidth=0
)

plt.title("Age Distribution of Customers", fontsize=16, weight='bold')
plt.xlabel("Age", fontsize=14)
plt.ylabel("Number of Customers", fontsize=14)
plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

# Plot count of each gender category
ax = sns.countplot(data=customer_data, x="Gender", palette="pastel")

# Add title and labels
ax.set_title("Customer Count by Gender", fontsize=16, weight='bold')
ax.set_xlabel("Gender", fontsize=14)
ax.set_ylabel("Number of Customers", fontsize=14)

# Optionally add percentages on top of bars
total = len(customer_data)
for p in ax.patches:
    count = p.get_height()
    percentage = f'{100 * count / total:.1f}%'
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    ax.text(x, y + 10, percentage, ha='center', fontsize=12)

plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

# Plot with regression and lowess smoothing, faceted by Gender
g = sns.lmplot(
    data=customer_data,
    x="Age",
    y="TotalPurchases",
    hue="Gender",
    palette="Set2",
    height=6,
    aspect=1.3,
    lowess=True,           # Smooth curve instead of just linear fit
    scatter_kws={"alpha":0.6, "s":40},
    line_kws={"lw":2}
)

g.set_axis_labels("Age", "Total Purchases")
plt.title("Age vs Total Purchases by Gender with LOWESS Smoothing", fontsize=16, weight='bold')
plt.tight_layout()
plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

plt.figure(figsize=(10, 6))
sns.violinplot(
    data=customer_data,
    x="Location",
    y="AverageOrderValue",
    inner=None,          # Hide default inner annotations to overlay boxplot
    palette="muted"
)

sns.boxplot(
    data=customer_data,
    x="Location",
    y="AverageOrderValue",
    width=0.15,
    palette="dark",
    showcaps=True,
    boxprops={'facecolor':'none'},
    showfliers=True,
    whiskerprops={'linewidth':1.5}
)

plt.title("Impact of Location on Average Order Value", fontsize=16, weight='bold')
plt.xlabel("Location")
plt.ylabel("Average Order Value ($)")
plt.show()

plt.figure(figsize=(10, 6))
sns.histplot(
    data=customer_data,
    x="LastPurchaseDaysAgo",
    hue="SubscriptionStatus",
    multiple="dodge",
    shrink=0.8,
    palette=["#1f77b4", "#ff7f0e"],
    bins=30,
    alpha=0.7
)

plt.title("Histogram of Days Since Last Purchase by Subscription Status", fontsize=16, weight='bold')
plt.xlabel("Days Since Last Purchase")
plt.ylabel("Count")
plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="ticks")

# Select columns to include
vars_to_plot = ["Age", "TotalPurchases", "AverageOrderValue", "LastPurchaseDaysAgo"]

# Create pairplot with hue for Gender
sns.pairplot(
    customer_data[vars_to_plot + ["Gender"]],
    hue="Gender",
    palette="Set2",
    diag_kind="kde",    # KDE for distribution on diagonals
    plot_kws={"alpha":0.6, "s":40},
    height=2.8
)

plt.suptitle("Pairwise Relationships between Customer Metrics by Gender", y=1.02, fontsize=16, weight='bold')
plt.show()
