import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

# Read the first CSV file
df1 = pl.read_csv("/1circle/1_circle_exp_10_1.csv")
df1 = df1.with_column(pl.lit(1).alias("site_id"))

# Perform aggregation on the first dataframe
df1 = (
    df1.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A")
            # pl.col("site_id").eq(1).sum().alias("site_B"),
            # pl.col("site_id").eq(2).sum().alias("site_C"),
            # pl.col("site_id").eq(3).sum().alias("site_D")
        ]
    )
    .with_columns((pl.col("site_A")/50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(17500)
)

# Read the second CSV file
df2 = pl.read_csv("/1circle/1_circle_exp_20_1.csv")
df2 = df2.with_column(pl.lit(2).alias("site_id"))

# Perform aggregation on the second dataframe
df2 = (
    df2.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A")
            # pl.col("site_id").eq(1).sum().alias("site_B"),
            # pl.col("site_id").eq(2).sum().alias("site_C"),
            # pl.col("site_id").eq(3).sum().alias("site_D")
        ]
    )
    .with_columns((pl.col("site_A")/50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(17500)
)

# Read the third CSV file
df3 = pl.read_csv("/1circle/1_circle_exp_40_1.csv")
df3 = df3.with_column(pl.lit(3).alias("site_id"))

# Perform aggregation on the third dataframe
df3 = (
    df3.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A")
            # pl.col("site_id").eq(1).sum().alias("site_B"),
            # pl.col("site_id").eq(2).sum().alias("site_C"),
            # pl.col("site_id").eq(3).sum().alias("site_D")
        ]
    )
    .with_columns((pl.col("site_A")/50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(17500)
)

# Concatenate the dataframes vertically
df_combined = pl.concat([df1, df2, df3])

# Create the line plot using Seaborn
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df_combined, x='frame', y='proportion', hue='site_id', ax=ax)

# Plot box plots along the line
sns.boxplot(data=df_combined, x='frame', y='proportion', hue='site_id', dodge=False, width=0.2, palette='Set3', showfliers=False, ax=ax)

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Convergence')
plt.title('Convergence over Time with Differing Detection Radius')

# Adjust legend position
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

# Show the plot
plt.show()