import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
#
file_paths = ["1circle_aggregation_radius_10_run_0.csv", "1circle_aggregation_radius_10_run_1.csv", "1circle_aggregation_radius_10_run_2.csv", "1circle_aggregation_radius_10_run_3.csv", "1circle_aggregation_radius_10_run_4.csv"]
file_paths2 = ["1circle_aggregation_radius_30_run_0.csv", "1circle_aggregation_radius_30_run_1.csv", "1circle_aggregation_radius_30_run_2.csv", "1circle_aggregation_radius_30_run_3.csv", "1circle_aggregation_radius_30_run_4.csv"]
file_paths1 = ["1circle_aggregation_radius_20_run_0.csv", "1circle_aggregation_radius_20_run_1.csv", "1circle_aggregation_radius_20_run_2.csv", "1circle_aggregation_radius_20_run_3.csv", "1circle_aggregation_radius_20_run_4.csv"]
file_paths3 = ["1circle_aggregation_radius_40_run_0.csv", "1circle_aggregation_radius_40_run_1.csv", "1circle_aggregation_radius_40_run_2.csv", "1circle_aggregation_radius_40_run_3.csv", "1circle_aggregation_radius_40_run_4.csv"]


# file_paths = ["4circle_aggregation_radius_10_run_0.csv", "4circle_aggregation_radius_10_run_1.csv", "4circle_aggregation_radius_10_run_2.csv", "4circle_aggregation_radius_10_run_3.csv", "4circle_aggregation_radius_10_run_4.csv"]
# file_paths2 = ["4_circle_exp_30_1.csv", "4_circle_exp_30_2.csv", "4_circle_exp_30_3.csv", "4_circle_exp_30_4.csv", "4_circle_exp_30_5.csv"]
# file_paths1 = ["4circle_aggregation_radius_20_run_0.csv", "4circle_aggregation_radius_20_run_1.csv", "4circle_aggregation_radius_20_run_2.csv", "4circle_aggregation_radius_20_run_3.csv", "4circle_aggregation_radius_20_run_4.csv"]
# file_paths3 = ["4circle_aggregation_radius_40_run_0.csv", "4circle_aggregation_radius_40_run_1.csv", "4circle_aggregation_radius_40_run_2.csv", "4circle_aggregation_radius_40_run_3.csv", "4circle_aggregation_radius_40_run_4.csv"]
dfs = []

for file_path in file_paths:
    df = pl.read_csv(file_path)
    df1= (
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
            pl.col("site_id").eq(1).sum().alias("site_B"),
            pl.col("site_id").eq(2).sum().alias("site_C"),
            pl.col("site_id").eq(3).sum().alias("site_D"),
        ]
    )
    .with_columns(((pl.col("site_A")+pl.col("site_B")+pl.col("site_C")+pl.col("site_D")) / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )
    dfs.append(df1)

merged_df1 = pl.concat(dfs)
pandas_df1 = merged_df1.to_pandas()
print(pandas_df1)


for file_path in file_paths1:
    df = pl.read_csv(file_path)
    df1= (
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
            pl.col("site_id").eq(1).sum().alias("site_B"),
            pl.col("site_id").eq(2).sum().alias("site_C"),
            pl.col("site_id").eq(3).sum().alias("site_D"),
        ]
    )
    .with_columns(((pl.col("site_A") + pl.col("site_B") + pl.col("site_C") + pl.col("site_D")) / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )
    dfs.append(df1)

merged_df2 = pl.concat(dfs)
pandas_df2 = merged_df2.to_pandas()
all_proportions = []
dataframes = [pandas_df1, pandas_df2]
print(pandas_df2)


for file_path in file_paths2:
    df = pl.read_csv(file_path)
    df1= (
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
            pl.col("site_id").eq(1).sum().alias("site_B"),
            pl.col("site_id").eq(2).sum().alias("site_C"),
            pl.col("site_id").eq(3).sum().alias("site_D"),
        ]
    )
    .with_columns(((pl.col("site_A") + pl.col("site_B") + pl.col("site_C") + pl.col("site_D")) / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )
    dfs.append(df1)

merged_df3 = pl.concat(dfs)
pandas_df3 = merged_df3.to_pandas()
print(pandas_df3)

for file_path in file_paths3:
    df = pl.read_csv(file_path)
    df1= (
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
            pl.col("site_id").eq(1).sum().alias("site_B"),
            pl.col("site_id").eq(2).sum().alias("site_C"),
            pl.col("site_id").eq(3).sum().alias("site_D"),
        ]
    )
    .with_columns(((pl.col("site_A")+pl.col("site_B")+pl.col("site_C")+pl.col("site_D")) / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )
    dfs.append(df1)

merged_df4 = pl.concat(dfs)
pandas_df4 = merged_df4.to_pandas()
print(pandas_df4)

dataframes = [pandas_df1, pandas_df2, pandas_df3, pandas_df4]
radius = 0
for i, df in enumerate(dataframes):
    # Group by the desired column (e.g., 'frame') and calculate the quartiles
    grouped_df = df.groupby('frame')['proportion'].quantile([0.5]).unstack()
    all_proportions.extend(grouped_df.values.flatten())
    # Plot the median line
    radius += 10
    plt.plot(grouped_df.index, grouped_df[0.5], label=f'Median of radius {radius}')



    #
    # # Plot the 25th percentile line
    # plt.plot(grouped_df.index, grouped_df[0.25], linestyle='--', label=f'25th percentile {i + 1}')
    #
    # # Plot the 75th percentile line
    # plt.plot(grouped_df.index, grouped_df[0.75], linestyle='--', label=f'75th percentile {i + 1}')

# Customize the plot
plt.xlabel('Frame')
plt.ylabel('Proportion')
plt.legend()
plt.title('Proportion Over Time in the One Food Segments environment')
plt.grid(True)
# Adjust y-axis limits
# Show the plot
plt.show()


# dataframes=[]
# dataframes.append(pandas_df1)
# dataframes.append(pandas_df2)
#
# combined_df = pd.concat(dataframes, keys=range(len(dataframes)))
#
# # Group by the desired column (e.g., 'frame') and calculate the quartiles
# grouped_df = combined_df.groupby('frame')['proportion'].quantile([0.25, 0.5, 0.75]).unstack()
#
# # Plot the median line
# plt.plot(grouped_df.index, grouped_df[0.5], color='red', label='Median')
#
# # Plot the 25th percentile line
# plt.plot(grouped_df.index, grouped_df[0.25], color='blue', linestyle='--', label='25th percentile')
#
# # Plot the 75th percentile line
# plt.plot(grouped_df.index, grouped_df[0.75], color='green', linestyle='--', label='75th percentile')
#
# # Customize the plot
# plt.xlabel('Frame')
# plt.ylabel('Proportion')
# plt.legend()
# plt.title('Proportion Over time')
# plt.grid(True)
#
# # Show the plot
# plt.show()
