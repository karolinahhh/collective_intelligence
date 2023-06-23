import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# file_paths = ["energy_run_0.csv","energy_run_1.csv","energy_run_2.csv","energy_run_3.csv","energy_run_4.csv","energy_run_5.csv","energy_run_6.csv","energy_run_7.csv","energy_run_8.csv","energy_run_9.csv","energy_run_10.csv","energy_run_11.csv","energy_run_12.csv","energy_run_13.csv","energy_run_14.csv","energy_run_15.csv","energy_run_16.csv","energy_run_17.csv","energy_run_18.csv","energy_run_19.csv"]
# file_paths = ["energy_free_run_0.csv","energy_free_run_1.csv","energy_free_run_2.csv","energy_free_run_3.csv","energy_free_run_4.csv","energy_free_run_5.csv","energy_free_run_6.csv","energy_free_run_7.csv","energy_free_run_8.csv","energy_free_run_9.csv","energy_free_run_10.csv","energy_free_run_11.csv","energy_free_run_12.csv","energy_free_run_13.csv","energy_free_run_14.csv","energy_free_run_15.csv","energy_free_run_16.csv","energy_free_run_17.csv","energy_free_run_18.csv","energy_free_run_19.csv"]
file_paths = ["energy_free_run_0.csv","energy_free_run_1.csv","energy_free_run_2.csv","energy_free_run_3.csv","energy_free_run_4.csv","energy_free_run_5.csv","energy_free_run_6.csv","energy_free_run_7.csv","energy_free_run_8.csv","energy_free_run_9.csv","energy_free_run_10.csv","energy_free_run_11.csv","energy_free_run_12.csv","energy_free_run_13.csv","energy_free_run_14.csv","energy_free_run_15.csv","energy_free_run_16.csv","energy_free_run_17.csv","energy_free_run_18.csv","energy_free_run_19.csv"]

range_df = pd.DataFrame(columns=["Predator_Range", "Prey_Range", "Proportion"])

for i in range(len(file_paths)):
    df = pl.read_csv(file_paths[i])
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
        .sort("simulated_seconds")
        .collect()
        )
    maxpred= max(df['pred_count'])
    maxprey= max(df['prey_count'])
    minpred= min(df['pred_count'])
    minprey= min(df['prey_count'])
    rangepred= maxpred-minpred
    rangeprey= maxprey-minprey
    proportion = rangeprey/rangepred

    range_df.loc[i, 'Predator_Range'] = rangepred
    range_df.loc[i, 'Prey_Range'] = rangeprey
    range_df.loc[i, 'Proportion'] = proportion

print(range_df)
range_df.to_excel("range_data_energy_free.xlsx", index=False)