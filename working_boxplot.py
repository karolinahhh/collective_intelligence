import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_paths = ["4_circle_exp_30_1.csv", "4_circle_exp_30_2.csv", "4_circle_exp_30_3.csv", "4_circle_exp_30_4.csv", "4_circle_exp_30_5.csv"]
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
        ]
    )
    .with_columns((pl.col("site_A") / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )
    dfs.append(df1)

merged_df = pl.concat(dfs)
print((merged_df))


pandas_df = merged_df.to_pandas()

quartiles = pandas_df.groupby('frame')['proportion'].quantile([0.25, 0.75]).unstack()
median = pandas_df.groupby('frame')['proportion'].median()

# Plot the lines for the quartiles and median
plt.plot(quartiles.index, quartiles[0.25], color='blue', label='25th percentile')
plt.plot(quartiles.index, quartiles[0.75], color='green', label='75th percentile')
plt.plot(median.index, median, color='red', label='Median')

# Set labels and title
plt.xlabel('Time')
plt.ylabel('Proportion')
plt.title('Proportion of aggregated agents over time (scenario 4-30)')

# Show legend
plt.legend()

# Show the plot
plt.show()
##################
# pandas_df.boxplot(by ='frame', column =['proportion'], grid = False)
# print(pandas_df)
#
# plt.savefig('4-30boxplot.png')#
##############
# quartiles = grouped_df['proportion'].quantile([0.25, 0.75]).unstack(level=-1)
# print(quartiles)
# # Convert the pandas DataFrame back to a Polars DataFrame
# quartiles_df = pl.from_pandas(quartiles)
# print(quartiles_df)
#
# # Plot the box plot
# quartiles_df.plot(kind="box")

# def calculate_quartiles(frame):
#     return frame.quantile([0.25, 0.75])["proportion"]
#
# quartiles = grouped_df.apply(calculate_quartiles)

# quartiles = grouped_df.quantile([0.25, 0.75]).select('proportion')
# quartiles = grouped_df.quantile([0.25, 0.75])["proportion"]
# quartiles.plot(kind="box")
# Perform the groupby and aggregation operations
# df = (
#     merged_df.lazy()
#     .groupby("frame")
#     .agg(
#         [
#             pl.col("site_id").is_null().sum().alias("no_site"),
#             pl.col("site_id").eq(0).sum().alias("site_A"),
#         ]
#     )
#     .with_columns((pl.col("site_A") / 50).alias("proportion"))
#     .sort("frame")
#     .collect()
#     .limit(17500)
# )
#
# # Convert Polars DataFrame to Pandas DataFrame
# pandas_df = grouped_df.to_pandas()
#
# # Create the box plot using Seaborn
# sns.boxplot(data=pandas_df, x='frame', y='proportion')
#
# # Set labels and title
# plt.xlabel('Frame')
# plt.ylabel('Proportion')
# plt.title('Box Plot of Proportion over Time')
#
# # Show the plot
# plt.show()