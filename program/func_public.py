#Everything to do with connecting to dydx through public requests

from constants import RESOLUTION
from func_utils import get_ISO_times
import pandas as pd
import numpy as np
import time

from pprint import pprint

#Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()
# pprint(ISO_TIMES)


# Get Candles recent
def get_candles_recent(client, market):

    #Define output
    close_prices = []

    #Protect API
    time.sleep(0.2)

    #Get data
    candles = client.public.get_candles(market=market, resolution=RESOLUTION, limit=100)

    #Structure data
    for candle in candles.data["candles"]:
        close_prices.append(candle["close"])

    # Construct and return close price series
    close_prices.reverse()
    prices_result = np.array(close_prices).astype(np.float)
    return prices_result


#Get Candles Historical
def get_candles_historical(client, market):

    #Define output
    close_prices = []

    #Extract historical price data for each timeframe. (gives us the keys of that dictrionary that we printed out earlier)
    for timeframe in ISO_TIMES.keys():

        #Confirm times needed
        tf_obj = ISO_TIMES[timeframe]
        from_iso = tf_obj["from_iso"]
        to_iso = tf_obj["to_iso"]

        #Protect rate limits/ API:
        time.sleep(0.2)

        #Get candlestick data from DYDX using the Public HTTP Endpoint ( see https://dydxprotocol.github.io/v3-teacher/#get-candles-for-market)
        candles = client.public.get_candles(
            market=market,
            resolution=RESOLUTION,
            from_iso=from_iso,
            to_iso=to_iso,
            limit=100
        )

        #Structure data
        for candle in candles.data["candles"]:
            close_prices.append({"datetime": candle["startedAt"], market: candle["close"] }) #close pricesa ppending with the timestamp that we want

        #Construct and return DataFrame
        close_prices.reverse() #we want our dataframe to have all the prices from old to new, we reverse the order so that we have them from old to new.
        return close_prices


#Construct market prices
def construct_market_prices(client):

    # Declare variables
    tradeable_markets =  []
    markets = client.public.get_markets() #list of all tickets that were available for trading

    # #Find tradeable pairs
    for market in markets.data["markets"].keys():
        market_info = markets.data["markets"][market] #we go through every single available market here and getting the object that relates to it for market info or callind that market info
        if market_info["status"] == "ONLINE" and market_info["type"] == "PERPETUAL":
            tradeable_markets.append(market)

    #Set initial DataFrame - store all the prices in that dataframe so that later we can see which ones are cointegrated
    close_prices = get_candles_historical(client, tradeable_markets[0]) #constrcut an initial dataframe, therefore [0]
    # pprint(close_prices)

    df = pd.DataFrame(close_prices)
    df.set_index("datetime", inplace=True)

    # print(df.head()) #head gives us the first five results

    # Append other prices to DataFrame
    # You can limit the amount to loop through here to save time in development
    for market in tradeable_markets[1:]:
        close_prices_add = get_candles_historical(client, market)
        df_add = pd.DataFrame(close_prices_add)
        df_add.set_index("datetime", inplace=True)
        df = pd.merge(df, df_add, how="outer", on="datetime", copy=False) #outer join; merge them together on based on the datetime
        del df_add #manage memory

    #Check any columns with NaNs (not a number)
    nans = df.columns[df.isna().any()].tolist()
    if len(nans) > 0:
        print("Dropping columns: ")
        print(nans)
        df.drop(columns=nans, inplace=True) #inplace means overwriting the existing df

    # Return result
    return df