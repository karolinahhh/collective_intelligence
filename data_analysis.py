import polars as pl

df = pl.read_csv("/Users/Karolynn/Desktop/ProjectCI/collective_intelligence/aggregation.csv")

print(
    df.lazy()
    .groupby("frame")
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no site"),
            pl.col("site_id").eq(0).sum().alias("site A"),
            pl.col("site_id").eq(1).sum().alias("site B")
        ]
    )
    .with_columns((pl.col("site A") / pl.com("site B")).alias("ratio"))
    .sort("frame")
    .collect()
)
