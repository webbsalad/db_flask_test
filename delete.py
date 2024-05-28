import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Input data
years = np.array([1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998])
tobacco_production = np.array([8,6.3,6.9,6.1,10.4,10,9.7,10.6,8.2,7.3,10,12.4,6.6,9.6,8.4,5.9,7.2,10.8,12.8])

# a) Plotting the time series
plt.figure(figsize=(10, 5))
plt.plot(years, tobacco_production, marker='o')
plt.title('a) Time series plot of tobacco production')
plt.xlabel('Year')
plt.ylabel('Production, thousand tons')
plt.grid(True)
plt.show()

# b) Calculating the first-order autocorrelation coefficient
autocorr = pearsonr(tobacco_production[:-1], tobacco_production[1:])[0]
print("b) First-order autocorrelation coefficient:", autocorr)

# c) Determining the trend equation type and calculating its parameters
# Since there is some trend visible in the plot, we'll use linear regression to approximate it
data = pd.DataFrame({'Year': years, 'Production': tobacco_production})

data['Year_Num'] = np.arange(1, len(data) + 1)

model = np.polyfit(data['Year_Num'], data['Production'], 1)

trend_slope = model[0]
trend_intercept = model[1]

print("c) Trend parameters (slope, intercept):", trend_slope, trend_intercept)

# d) Interpreting trend parameters and conclusions
if trend_slope > 0:
    trend_interpretation = "Tobacco production is increasing over time."
elif trend_slope < 0:
    trend_interpretation = "Tobacco production is decreasing over time."
else:
    trend_interpretation = "Tobacco production remains constant over time."

print("d) Interpretation of trend parameters and conclusions:", trend_interpretation)
