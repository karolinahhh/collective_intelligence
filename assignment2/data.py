import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_path= "predprey.csv"

df = pl.read_csv(file_path)
df=(
    df.lazy()
    .with_columns((pl.col("frame") / 60).alias("simulated_seconds"))
    .groupby(pl.col("simulated_seconds"))

    .agg(
        [
            pl.col("agent").eq(0).sum().alias("pred_count"),
            pl.col("agent").eq(1).sum().alias("prey_count"),
            pl.col("id").count().alias("total count"),
        ]
    )
    # .with_columns(((pl.col("site_A")+pl.col("site_B")+pl.col("site_C")+pl.col("site_D")) / 50).alias("proportion"))
    .sort("simulated_seconds")
    .collect()
    # .limit(15000)
    )

df.to_csv("ampli.csv")

# Plotting
plt.plot(df['simulated_seconds'], df['pred_count'], label='Predator Count')
plt.plot(df['simulated_seconds'], df['prey_count'], label='Prey Count')
plt.xlabel('Simulated_seconds')
plt.ylabel('Count')
plt.title('Predator and Prey Count Over Time')
plt.legend()

# Display the plot
plt.show()