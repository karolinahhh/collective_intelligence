import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_pattern = "camouflage_{}.csv"
num_files = 50

# Read and merge the CSV files
dfs = []
for i in range(num_files):
    file_path = file_pattern.format(i)
    df = pl.read_csv(file_path)
    df1 = (
        df.lazy()
        .with_columns((pl.col("frame") / 60).alias("simulated_seconds"))
        .groupby(pl.col("simulated_seconds"))
        .agg(
            [
                pl.col("agent").eq(0).sum().alias("pred_count"),
                pl.col("agent").eq(1).sum().alias("prey_count"),
            ]
        )
        .sort("simulated_seconds")
        .collect()
    )
    dfs.append(df1)

merged_df1 = pl.concat(dfs)
pandas_df1 = merged_df1.to_pandas()

# Group by simulated_seconds and calculate median and standard deviation
pred_median = pandas_df1.groupby('simulated_seconds')['pred_count'].mean()
pred_std = pandas_df1.groupby('simulated_seconds')['pred_count'].std()
prey_median = pandas_df1.groupby('simulated_seconds')['prey_count'].mean()
prey_std = pandas_df1.groupby('simulated_seconds')['prey_count'].std()

# Set seaborn style
sns.set(style='darkgrid')

# Plotting
plt.figure(figsize=(10, 6))
sns.lineplot(data=pred_median, label='Predator Median')
sns.lineplot(data=prey_median, label='Prey Median')
# plt.fill_between(pred_median.index, pred_median - pred_std, pred_median + pred_std, alpha=0.3)
# plt.fill_between(prey_median.index, prey_median - prey_std, prey_median + prey_std, alpha=0.3)
plt.xlabel('Simulated Seconds')
plt.ylabel('Median')
plt.title('Predator and Prey Median Count Over Time')
plt.legend()

# Display the plot
plt.show()

print("Predator Median:")
print(pred_median)
print("Predator Standard Deviation:")
print(pred_std)
print("Prey Median:")
print(prey_median)
print("Prey Standard Deviation:")
print(prey_std)
