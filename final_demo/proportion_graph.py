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
    df1= (
    df.lazy()
    .with_columns((pl.col("frame") / 60).alias("simulated_seconds"))
    .groupby(pl.col("simulated_seconds"))
    .agg(
        [
            # pl.col("prey type").eq(0).sum().alias("red_count"),
            # pl.col("prey type").eq(1).sum().alias("green_count"),
            # pl.col("prey type").eq(2).sum().alias("pred_count"),
            # pl.col("id").count().alias("total count"),
            pl.col("agent").eq(0).sum().alias("pred_count"),
            pl.col("agent").eq(1).sum().alias("prey_count"),
            # pl.col("id").count().alias("total count"),

        ]
    )
    .with_columns((pl.col("prey_count") / pl.col("pred_count")).alias("proportion"))
    .sort("simulated_seconds")
    .collect()

    )
    dfs.append(df1)

merged_df1 = pl.concat(dfs)
pandas_df1 = merged_df1.to_pandas()
print(pandas_df1)


# Group by simulated_seconds and calculate median
# pred_median = pandas_df1.groupby('simulated_seconds')['pred_count'].median()
# red_median = pandas_df1.groupby('simulated_seconds')['red_count'].median()
# green_median = pandas_df1.groupby('simulated_seconds')['green_count'].median()
pred_median = pandas_df1.groupby('simulated_seconds')['pred_count'].median()
prey_median = pandas_df1.groupby('simulated_seconds')['prey_count'].median()
prop_median = pandas_df1.groupby('simulated_seconds')['proportion'].median()
# Plotting
# plt.plot(pred_median.index, pred_median.values, label='Predator Median')
# plt.plot(prey_median.index, prey_median.values, label='Prey Median')
plt.plot(prop_median.index, prop_median.values, label='Proportion of Prey to Predator')
plt.xlabel('Simulated Seconds')
plt.ylabel('Proportion')
plt.title('Camouflage Scenario: Predator and Prey Proportion Over Time')
plt.legend()

# plt.ylim(0, 700)
# Display the plot
plt.show()
#
# print("Predator Median:")
# print(pred_median)
# print("Prey Median:")
# print(prey_median)
# print("Red Median:")
# print(red_median)
# print("Green Median:")
# print(green_median)