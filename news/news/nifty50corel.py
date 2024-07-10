import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import statsmodels.api as sm

nifty_assets = [
    "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TCS.NS",

]
market_index = '^NSEI'  # Nifty 50

# Step 2: Fetch Historical Data
start_date = "2023-06-06"
end_date = "2024-06-06"
data = yf.download(nifty_assets + [market_index], start=start_date, end=end_date)['Adj Close']

# Step 3: Calculate Daily Returns
returns = data.pct_change().dropna()

cor_matrix = returns.corr()





if data.isnull().values.any():
    print("Data contains missing values. Handling missing data...")
    data = data.fillna(method='ffill').fillna(method='bfill')  # Forward fill, then backward fill

print(cor_matrix)
# Step 6: Save Correlation Matrix to Excel
output_file = "Nifty50_Correlation_Matrix.xlsx"
cor_matrix.to_excel(output_file)

print(f"Correlation matrix saved to {output_file}")
