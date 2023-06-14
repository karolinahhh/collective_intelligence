import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt


df = pl.read_csv("four_circles_trial1.csv")

df=(
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
            pl.col("site_id").eq(1).sum().alias("site_B"),
            pl.col("site_id").eq(2).sum().alias("site_C"),
            pl.col("site_id").eq(3).sum().alias("site_D")
        ]
    )
    #.with_columns((abs(pl.col("site_A") - pl.col("site_B"))).alias("absolute_value"))
    # .with_columns((pl.col("site_A")/50).alias("proportion"))
    .with_columns(((pl.col("site_A")+pl.col("site_B")+pl.col("site_C")+pl.col("site_D"))/50).alias("proportion"))

    .sort("frame")
    .collect()
    # .limit(12500)

)


# Create the line plot using Seaborn
sns.lineplot(data=df, x='frame', y='absolute_value')

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Absolute Value')
plt.title('Absolute Value over Time')

# Show the plot
plt.show()