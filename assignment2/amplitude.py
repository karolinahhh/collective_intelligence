import numpy as np
import pandas as pd
from scipy.signal import correlate, find_peaks
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl

data = pd.read_csv('ampli.csv')

values = data['pred_count'].values
window_size = 200
moving_average = data['pred_count'].rolling(window=window_size, center=True).mean()
print(moving_average)
# plt.plot(data['pred_count'], label='Original Data')
# plt.plot(moving_average, label='Moving Average (Window Size={})'.format(window_size))
# plt.xlabel('Frame')
# plt.ylabel('Count')
# plt.legend()
# plt.show()

###############
# autocorr = correlate(values, values, mode='same')
#
# # Plot the autocorrelation
# plt.plot(autocorr)
# plt.xlabel('Lag')
# plt.ylabel('Autocorrelation')
# plt.show()
#
# # Find the peaks in the autocorrelation to determine the periodicity
# peaks, _ = find_peaks(autocorr)
# period = np.diff(peaks)[0]  # Assuming the first peak corresponds to one period
#
# print("Estimated period length:", period)
################
# mean_value = np.mean(values)
#
# peaks, _ = find_peaks(values)
#
# amplitudes = values[peaks] - mean_value
# print(amplitudes)
#
# a= max(amplitudes)
# print(a)

