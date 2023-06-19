import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

file_paths = ["1_circle_exp_30_1.csv", "1_circle_exp_30_2.csv", "1_circle_exp_30_3.csv", "1_circle_exp_30_4.csv", "1_circle_exp_30_5.csv"]

dfs = []

for file_path in file_paths:
    df = pl.read_csv(file_path)
    dfs.append(df)

merged_df = pl.concat(dfs)

grouped_df = (
    merged_df.lazy()
    .groupby(["frame", "file"])  # Group by both "frame" and "file"
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
        ]
    )
    .with_columns((pl.col("site_A") / 50).alias("proportion"))
    .sort(["frame", "file"])  # Sort by both "frame" and "file"
    .collect()
    .limit(17500)
)

df = grouped_df.to_pandas()

plt.boxplot(df['proportion'], positions=df['frame'], widths=0.6)

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Proportion')
plt.title('Box Plot of Simulation Results')

# Show the plot
plt.show()
