import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import statsmodels.api as sm

# Step 1: Select Assets and Market Index
nifty_assets = ['ZOMATO.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS', 'TATAMOTORS.NS',
                'M&M.NS','LT.NS','HAL.NS','ONGC.NS','INDIGO.NS', 'ITC.NS','MCX.NS' , 'GOLD.AX']
market_index = '^NSEI'  # Nifty 50

# Step 2: Fetch Historical Data
start_date = "2023-06-06"
end_date = "2024-06-06"
data = yf.download(nifty_assets + [market_index], start=start_date, end=end_date)['Adj Close']

# Step 3: Calculate Daily Returns
returns = data.pct_change().dropna()

# Step 4: Calculate Expected Returns and Covariance Matrix
expected_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252
cor_matrix = returns.corr().round(2)
# Step 5: Define Portfolio Metrics
def portfolio_performance(weights, expected_returns, cov_matrix):
    returns = np.dot(weights, expected_returns[:-1])  # Exclude the market index return
    risk = np.sqrt(np.dot(weights, np.dot(cov_matrix.iloc[:-1, :-1], weights)))
    return returns, risk

# Step 6: Optimize Portfolio
def minimize_risk(weights, expected_returns, cov_matrix):
    return portfolio_performance(weights, expected_returns, cov_matrix)[1]

constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
bounds = tuple((0, 1) for _ in range(len(nifty_assets)))
initial_weights = [1./len(nifty_assets) for _ in range(len(nifty_assets))]

optimal_result = minimize(minimize_risk, initial_weights, args=(expected_returns, cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)
optimal_weights = optimal_result.x
optimal_weights = [0.05,0.15,0.05,0.1,0.1,0.1,0.1,0.1,0.05,0.05,.05,0.05,0.05]
# Step 7: Calculate Optimal Portfolio Performance
optimal_returns, optimal_risk = portfolio_performance(optimal_weights, expected_returns, cov_matrix)

# Step 8: Calculate Beta of Each Stock
market_returns = returns[market_index]
betas = []

for stock in nifty_assets:
    stock_returns = returns[stock]
    X = sm.add_constant(market_returns)
    model = sm.OLS(stock_returns, X).fit()
    betas.append(model.params[1])

# Step 9: Calculate Portfolio Beta
portfolio_beta = np.dot(optimal_weights, betas)

# Display Results
print("Optimal Weights:", optimal_weights)
print("Expected Portfolio Return:", optimal_returns)
print("Expected Portfolio Risk:", optimal_risk)
print("Portfolio Beta:", portfolio_beta)
print("cov matrix", cor_matrix)

output_file = "Nifty50_Correlation_Matrix.xlsx"
cor_matrix.to_excel(output_file)

import numpy as np

# Assuming these are annualized returns and risk-free rate (e.g., 1-year Treasury yield)
annual_risk_free_rate = 0.06

# Sharpe Ratio
sharpe_ratio = (optimal_returns - annual_risk_free_rate) / optimal_risk

# Treynor Ratio
# Assuming market return of 8% and portfolio beta of 1 (you can adjust based on your portfolio beta)
market_return = 0.08
#portfolio_beta = 1
treynor_ratio = (optimal_returns - annual_risk_free_rate) / portfolio_beta

# Jensen's Alpha
jensens_alpha = optimal_returns - (annual_risk_free_rate + portfolio_beta * (market_return - annual_risk_free_rate))

alpha = optimal_returns - annual_risk_free_rate - portfolio_beta * (market_return - annual_risk_free_rate)

print("Sharpe Ratio:", sharpe_ratio)
print("Treynor Ratio:", treynor_ratio)
print("Jensen's Alpha:", jensens_alpha)
print("Alpha:", alpha)


# Plot Efficient Frontier
num_portfolios = 10000
results = np.zeros((3, num_portfolios))

for i in range(num_portfolios):
    weights = np.random.random(len(nifty_assets))
    weights /= np.sum(weights)
    portfolio_return, portfolio_risk = portfolio_performance(weights, expected_returns, cov_matrix)
    results[0,i] = portfolio_risk
    results[1,i] = portfolio_return
    results[2,i] = results[1,i] / results[0,i]

plt.figure(figsize=(10, 7))
plt.scatter(results[0,:], results[1,:], c=results[2,:], cmap='viridis', marker='o')
plt.xlabel('Expected Risk')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe Ratio')
plt.scatter(optimal_risk, optimal_returns, c='red', marker='*', s=100)
plt.title('Efficient Frontier')
plt.show()






'''
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import time

# Step 1: Select Assets
assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JNJ']

# Step 2: Fetch Historical Data with Error Handling
def fetch_data(ticker, start, end):
    for _ in range(5):  # Retry up to 5 times
        try:
            data = yf.download(ticker, start=start, end=end)['Adj Close']
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            time.sleep(1)  # Wait for 1 second before retrying
    return None

start_date = "2021-01-01"
end_date = "2023-01-01"
data = pd.DataFrame()

for asset in assets:
    asset_data = fetch_data(asset, start_date, end_date)
    if asset_data is not None:
        data[asset] = asset_data

# Check if we have data for all assets
if data.isnull().values.any():
    print("Some data could not be fetched. Exiting.")
else:
    # Step 3: Calculate Daily Returns and Expected Returns
    returns = data.pct_change().dropna()
    expected_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    # Step 4: Define Portfolio Metrics
    def portfolio_performance(weights, expected_returns, cov_matrix):
        returns = np.dot(weights, expected_returns)
        risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return returns, risk

    # Step 5: Optimize Portfolio
    def minimize_risk(weights, expected_returns, cov_matrix):
        return portfolio_performance(weights, expected_returns, cov_matrix)[1]

    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
    bounds = tuple((0, 1) for _ in range(len(assets)))
    initial_weights = [1./len(assets) for _ in range(len(assets))]

    optimal_result = minimize(minimize_risk, initial_weights, args=(expected_returns, cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = optimal_result.x

    # Calculate Optimal Portfolio Performance
    optimal_returns, optimal_risk = portfolio_performance(optimal_weights, expected_returns, cov_matrix)

    # Display Results
    print("Optimal Weights:", optimal_weights)
    print("Expected Portfolio Return:", optimal_returns)
    print("Expected Portfolio Risk:", optimal_risk)

    # Plot Efficient Frontier
    num_portfolios = 10000
    results = np.zeros((3, num_portfolios))

    for i in range(num_portfolios):
        weights = np.random.random(len(assets))
        weights /= np.sum(weights)
        portfolio_return, portfolio_risk = portfolio_performance(weights, expected_returns, cov_matrix)
        results[0,i] = portfolio_risk
        results[1,i] = portfolio_return
        results[2,i] = results[1,i] / results[0,i]

    plt.figure(figsize=(10, 7))
    plt.scatter(results[0,:], results[1,:], c=results[2,:], cmap='viridis', marker='o')
    plt.xlabel('Expected Risk')
    plt.ylabel('Expected Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.scatter(optimal_risk, optimal_returns, c='red', marker='*', s=100)
    plt.title('Efficient Frontier')
    plt.show()
'''