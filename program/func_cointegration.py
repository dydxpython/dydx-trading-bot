import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from constants import MAX_HALF_LIFE, WINDOW

# Calculate Half Life
# https://www.pythonforfinance.net/2016/05/09/python-backtesting-mean-reversion-part-2/
def calculate_half_life(spread):
    df_spread = pd.DataFrame(spread, columns=["spread"])
    spread_lag = df_spread.spread.shift(1) #shift up one, it takes the row above; shift minus one shifts to the row in teh future.
    spread_lag.iloc[0] = spread_lag.iloc[1]
    spread_ret = df_spread.spread - spread_lag
    spread_ret.iloc[0] = spread_ret.iloc[1]
    spread_lag2 = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret, spread_lag2)
    res = model.fit()
    halflife = round(-np.log(2) / res.params[1], 0)
    return halflife


#Calculate ZScore of the spread (take a point from that dataframe and calculate the zscore from that point)
#The zscore is a trigger for deciding if we go to our constants when to exit/enter a trade.
def calculate_zscore(spread):
    spread_series = pd.Series(spread)
    mean = spread_series.rolling(center=False, window=WINDOW).mean()
    std = spread_series.rolling(center=False, window=WINDOW).std()
    x = spread_series.rolling(center=False, window=1).mean()
    zscore = (x - mean) / std
    return zscore

#Calculate Cointegration; for a better method see https://www.udemy.com/course/dydx-pairs-trading-bot-build-in-python-running-in-the-cloud/learn/lecture/41200738#questions/19125198 (however it raises an error for me)
def calculate_cointegration(series_1, series_2):
    series_1 = np.array(series_1).astype(np.float) #make sure that we're consistently passing our series in as a float to our stats model's function
    series_2 = np.array(series_2).astype(np.float)
    coint_flag = 0
    coint_res = coint(series_1, series_2)
    coint_t = coint_res[0]
    p_value = coint_res[1] #if the p-value is less than 0.05, then this is co-integrated
    critical_value = coint_res[2][1]
    model = sm.OLS(series_1, series_2).fit()
    hedge_ratio = model.params[0]
    spread = series_1 - (hedge_ratio * series_2)
    half_life = calculate_half_life(spread)
    t_check = coint_t < critical_value #t value should be less than the critical value to be co-integrated. Some would not agree with the teacher
    coint_flag = 1 if p_value < 0.05 and t_check else 0
    return coint_flag, hedge_ratio, half_life

#Store cointegration Results
def store_cointegration_results(df_market_prices):

    #Initialize
    markets = df_market_prices.columns.to_list() #gives us the columns in a list
    criteria_met_pairs = []

    #Find cointegrated pairs
    #start with our base pair
    #loop through all of these prices in df_market_prices dataframe  and run them through our co-integration function (the first is our base pair, check all others, then go to the next as base pair and do the same etc.) (base and quotes)
    for index, base_market in enumerate(markets[:-1]):
        series_1 = df_market_prices[base_market].values.astype(float).tolist()

        #Get Quote Pair
        for quote_market in markets[index + 1:]:
            series_2 = df_market_prices[quote_market].values.astype(float).tolist()

            #Check cointegration
            coint_flag, hedge_ratio, half_life = calculate_cointegration(series_1, series_2)

            #Log pair
            if coint_flag == 1 and half_life <= MAX_HALF_LIFE and half_life > 0:
                criteria_met_pairs.append({
                    "base_market": base_market,
                    "quote_market": quote_market,
                    "hedge_ratio": hedge_ratio,
                    "half_life": half_life,
                })

    # Create and save DataFrame
    df_criteria_met = pd.DataFrame(criteria_met_pairs)
    df_criteria_met.to_csv("cointegrated_pairs.csv")
    del df_criteria_met

    #Return result
    print("Cointegrated pairs successfully saved")
    return "saved"
