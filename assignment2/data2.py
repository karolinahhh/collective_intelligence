import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_path= "energy_run_0.csv"

df = pl.read_csv(file_path)
df=(
# print(
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("agent").eq(0).sum().alias("pred_count"),
            pl.col("agent").eq(1).sum().alias("prey_count"),
            pl.col("id").count().alias("total count"),
            pl.col("prey consumed").sum().alias("preyconsumed")
        ]
    )
    .with_columns((pl.col("prey_count")/pl.col("total count")).alias("prey_density"))
    .sort("frame")
    .collect()
    # .limit(15000)
    )
pandas_df = df.to_pandas()
pandas_df['groupid'] = None

for i in range(len(pandas_df["frame"])):
    temp= pandas_df["frame"][i]//20
    pandas_df["groupid"][i] = temp

# print(pandas_df)
polars_df = pl.from_pandas(pandas_df)
grouped_df=(
    polars_df.lazy()
    .groupby("groupid")
    .agg(
        [
            pl.col("preyconsumed").sum().alias("preyconsumed1"),
            pl.col("prey_count").mean().alias("prey_density1")
        ]
    )
    .collect()
    )
print(grouped_df)


plt.scatter(grouped_df['prey_density1'], grouped_df['preyconsumed1'])
plt.xlabel('Prey Density')
plt.ylabel('Number of Prey Consumed')
plt.title('Relationship between Prey Density and Prey Consumption')
plt.show()


