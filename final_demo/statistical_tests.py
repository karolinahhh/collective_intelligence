import polars as pl
from scipy.stats import ttest_ind, ranksums

# Read the count data from CSV files or DataFrame creation

# Scenario 1: Energy factor used
df_scenario1 = pl.read_csv("scenario1.csv")  # put the name of the merged csv

# Scenario 2: No energy factor
df_scenario2 = pl.read_csv("scenario2.csv")  # put the name of the merged csv

# Extract the count columns from the DataFrames
count_scenario1 = df_scenario1['count']  # change the name of the column
count_scenario2 = df_scenario2['count']

# Perform t-test
t_stat, p_value_ttest = ttest_ind(count_scenario1, count_scenario2)

# Perform Wilcoxon rank-sum test
z_stat, p_value_ranksum = ranksums(count_scenario1, count_scenario2)

# Print the results
print("T-test: ")
print("T-statistic:", t_stat)
print("P-value:", p_value_ttest)

print("\nWilcoxon Rank-Sum Test: ")
print("Z-statistic:", z_stat)
print("P-value:", p_value_ranksum)
