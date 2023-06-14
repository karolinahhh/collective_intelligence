import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt


df = pl.read_csv("aggregation.csv")

df=(
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no site"),
            pl.col("site_id").eq(0).sum().alias("site A"),
            pl.col("site_id").eq(1).sum().alias("site B")
        ]
    )
    .with_columns(abs(pl.col("site A") - pl.col("site B")).alias("absolute_value"))
    .sort("frame")
    .collect()
)

# Create the line plot using Seaborn
sns.lineplot(data=df, x='frame', y='absolute_value')

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Absolute Value')
plt.title('Absolute Value over Time')

# Show the plot
plt.show()