import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_path= "predprey.csv"

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
df = df.with_column("group_id", df['frame'] // 50)

# Group the DataFrame by the group_id
grouped_df = df.groupby("group_id").agg(
    {
        "frame": pl.first("frame"),  # You can choose any column for aggregation
        "pred_count": pl.sum("pred_count"),
        "prey_count": pl.sum("prey_count"),
        "total count": pl.sum("total count"),
        "preyconsumed": pl.sum("preyconsumed"),
        "prey_density": pl.mean("prey_density")
    }
)
print(grouped_df)

# grouped_df = df.groupby(df['frame'] // 50).agg(
#     {
#         'preyconsumed': pl.sum(pl.col('preyconsumed')),
#         'prey_density': pl.mean(pl.col('prey_density'))
#     }
# )
# grouped_df = grouped_df.with_column('avg_prey_density', grouped_df['prey_density'].mean())
# print(grouped_df)
plt.plot(df['prey_density'], df['preyconsumed'])
plt.xlabel('Prey Density')
plt.ylabel('Number of Prey Consumed')
plt.title('Relationship between Prey Density and Prey Consumption')
plt.show()
# plt.scatter(df['prey_density'], df['preyconsumed'],kind='line')
# plt.xlabel('Prey Density')
# plt.ylabel('Number of Prey Consumed')
# plt.title('Relationship between Prey Density and Prey Consumption')
# plt.show()
#
# # Plotting
# plt.plot(df['frame'], df['pred_count'], label='Predator Count')
# plt.plot(df['frame'], df['prey_count'], label='Prey Count')
# plt.xlabel('Frame')
# plt.ylabel('Count')
# plt.title('Predator and Prey Count Over Time')
# plt.legend()
#
# # Display the plot
# plt.show()

