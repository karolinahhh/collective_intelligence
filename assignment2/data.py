import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_path= "predprey_no_energy.csv"

df = pl.read_csv(file_path)
df=(
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("agent").eq(0).sum().alias("pred_count"),
            pl.col("agent").eq(1).sum().alias("prey_count"),
            pl.col("id").count().alias("total count"),
        ]
    )
    # .with_columns(((pl.col("site_A")+pl.col("site_B")+pl.col("site_C")+pl.col("site_D")) / 50).alias("proportion"))
    .sort("frame")
    .collect()
    .limit(15000)
    )

# Plotting
plt.plot(df['frame'], df['pred_count'], label='Predator Count')
plt.plot(df['frame'], df['prey_count'], label='Prey Count')
plt.xlabel('Frame')
plt.ylabel('Count')
plt.title('Predator and Prey Count Over Time')
plt.legend()

# Display the plot
plt.show()