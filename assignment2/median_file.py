import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_pattern = "freeze_fear_{}.csv"
num_files = 20

# Read and merge the CSV files
dfs = []
for i in range(num_files):
    file_path = file_pattern.format(i)
    df = pl.read_csv(file_path)
    df1= (
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
print(pandas_df1)


# Group by simulated_seconds and calculate median
pred_median = pandas_df1.groupby('simulated_seconds')['pred_count'].mean()
prey_median = pandas_df1.groupby('simulated_seconds')['prey_count'].mean()

# Plotting
plt.plot(pred_median.index, pred_median.values, label='Predator Median')
plt.plot(prey_median.index, prey_median.values, label='Prey Median')
plt.xlabel('Simulated Seconds')
plt.ylabel('Median')
plt.title('Predator and Prey Median Count Over Time')
plt.legend()

# Display the plot
plt.show()

print("Predator Median:")
print(pred_median)
print("Prey Median:")
print(prey_median)
