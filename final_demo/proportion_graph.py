import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


file_pattern = "safety_starvation_{}.csv"
num_files = 30

# Read and merge the CSV files
dfs = []
end_times = []  # Store the end times for each case
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

    # Find the last simulated second for each case
    last_second = df1["simulated_seconds"].max()
    end_times.append(last_second)

merged_df1 = pl.concat(dfs)
pandas_df1 = merged_df1.to_pandas()

# Group by simulated_seconds and calculate median
pred_median = pandas_df1.groupby('simulated_seconds')['pred_count'].median()
prey_median = pandas_df1.groupby('simulated_seconds')['prey_count'].median()

# Plotting
plt.plot(pred_median.index, pred_median.values, label='Predator Median')
plt.plot(prey_median.index, prey_median.values, label='Prey Median')
plt.xlabel('Simulated Seconds')
plt.ylabel('Median')
plt.title('Safety with fear Scenario: Predator and Prey Median Over Time')
plt.legend()
# plt.ylim(0, 190)

# Save the end times to an Excel file
end_times_df = pd.DataFrame({'Case': range(num_files), 'End Time (Simulated Seconds)': end_times})
end_times_df.to_excel('safety_with_fear_end_times.xlsx', index=False)

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