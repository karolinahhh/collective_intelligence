import numpy as np
import pandas as pd
from scipy.signal import correlate, find_peaks
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl

data = pd.read_csv('ampli.csv')

values1 = data['pred_count'].values
values2 = data['prey_count'].values

mean_value1 = np.mean(values1)
mean_value2 = np.mean(values2)

peaks1, _ = find_peaks(values1)
peaks2, _ = find_peaks(values2)

amplitudes1 = values1[peaks1] - mean_value1
amplitudes2 = values2[peaks2] - mean_value2

a= max(amplitudes1)
b= max(amplitudes2)
print("Amplitude of predator:", a)
print("Amplitude of predator:", b)


# window_size = 200
# moving_average = data['pred_count'].rolling(window=window_size, center=True).mean()
# print(moving_average)

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
# values1 = data['pred_count'].values
# values2 = data['prey_count'].values
#
# mean_value1 = np.mean(values1)
# mean_value2 = np.mean(values2)
#
# peaks1, _ = find_peaks(values1)
# peaks2, _ = find_peaks(values2)
#
# amplitudes1 = values1[peaks1] - mean_value1
# amplitudes2 = values2[peaks2] - mean_value2
#
# a= max(amplitudes1)
# b= max(amplitudes2)
# print("Amplitude of predator:", a)
# print("Amplitude of predator:", b)

