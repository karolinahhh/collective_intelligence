import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

file_paths = ["1_circle_exp_30_1.csv", "1_circle_exp_30_2.csv", "1_circle_exp_30_3.csv", "1_circle_exp_30_4.csv", "1_circle_exp_30_5.csv"]
dfs = []

for file_path in file_paths:
    df = pl.read_csv(file_path)
    # Add a "file" column with the current file name
    df = df.with_column(pl.lit(file_path).alias("file"))
    dfs.append(df)

# Concatenate the DataFrames from all files into a single DataFrame
merged_df = pl.concat(dfs)

# Perform the groupby and aggregation operations
grouped_df = (
    merged_df.lazy()
    .groupby(["frame", "file"])  # Group by both "frame" and "file"
    .agg(
        [
            pl.col("site_id").is_null().sum().alias("no_site"),
            pl.col("site_id").eq(0).sum().alias("site_A"),
        ]
    )
    .with_column((pl.col("site_A") / 50).alias("proportion"))
    .sort(["frame", "file"])  # Sort by both "frame" and "file"
    .collect()
    .limit(17500)
)

# Convert Polars DataFrame to Pandas DataFrame
pandas_df = grouped_df.to_pandas()

# Create the box plot using Seaborn
sns.boxplot(data=pandas_df, x='frame', y='proportion', hue='file')

# Calculate additional boxplot statistics
medians = pandas_df.groupby(['frame', 'file'])['proportion'].median().values
q1 = pandas_df.groupby(['frame', 'file'])['proportion'].quantile(0.25).values
q3 = pandas_df.groupby(['frame', 'file'])['proportion'].quantile(0.75).values

# Add the additional boxplot elements to the plot
ax = sns.boxplot(data=pandas_df, x='frame', y='proportion', hue='file')
ax.plot(range(len(medians)), medians, color='r', linestyle='-', label='Median')
ax.plot(range(len(q1)), q1, color='g', linestyle='--', label='Q1')
ax.plot(range(len(q3)), q3, color='b', linestyle='--', label='Q3')
ax.legend()

# Set labels and title
plt.xlabel('Frame')
plt.ylabel('Proportion')
plt.title('Box Plot of Proportion over Time')

# Show the plot
plt.show()
