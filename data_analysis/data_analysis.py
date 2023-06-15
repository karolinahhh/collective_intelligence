import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

file_paths = ["1_circle_exp_30_1.csv", "1_circle_exp_30_2.csv", "1_circle_exp_30_3.csv", "1_circle_exp_30_4.csv", "1_circle_exp_30_5.csv"]
dfs = []

for file_path in file_paths:
    df = pl.read_csv(file_path)
    dfs.append(df)

# Concatenate the DataFrames from all files into a single DataFrame
merged_df = pl.concat(dfs)

# Perform the groupby and aggregation operations
grouped_df = (
    merged_df.lazy()
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
    .limit(17500)
)

# Convert Polars DataFrame to Pandas DataFrame
pandas_df = grouped_df.to_pandas()

# Create the box plot using Seaborn
sns.boxplot(data=pandas_df, x='frame', y='proportion')

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Proportion')
plt.title('Box Plot of Proportion over Time')

# Show the plot
plt.show()