##Bot Constants Configuration Setup

from dydx3.constants import API_HOST_SEPOLIA, API_HOST_MAINNET
#Enable us to access our environment variables
from decouple import config

# !!! SELECT MODE !!!
MODE = "DEVELOPMENT"

#Close all open positions and orders. Trigger that if we set it will close all open positions if True; if false it won't
ABORT_ALL_POSITIONS = False

#Find Cointegrated Pairs. Tell bot to do a fresh view of what pairs are cointegrated
FIND_COINTEGRATED = True

# Manage Exits
MANAGE_EXITS = True

# Place Trades; true if we want to place trades
PLACE_TRADES = True

#Resolution (here: hourly timeframe trading)
RESOLUTION = "1HOUR"

#Stats Window (calculating the z-score we need to calculate a rolling average; do a rolling moving average based on 21 days)
WINDOW = 21

#Thresholds - Opening a Trade. 50 USD per trade. USD_MIN_COLLATERAL should be around the balance in the account
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5
USD_PER_TRADE = 50
USD_MIN_COLLATERAL = 1880

#Thresholds for Closing
CLOSE_AT_ZSCORE_CROSS = True

#Ethereum Address
ETHEREUM_ADDRESS = "0x6EF109e276680BfE65B3FD9B5E335D65BB9886E9" #copy it from Metamask

#KEYS -PRODUCTION
#Must to be on Mainnet on DYDX
#Config knows how to go and actually get this value from environment variables or an environment variables file that has
# been set up on your machine. So when we run this in the cloud, we will create an environment variable there rather
# than storing these in GitHub and it will know how to go and get those.
STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")

#KEYS -DEVELOPMENT
#Must to be on Testnet on DYDX
STARK_PRIVATE_KEY_TESTNET = config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET = config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET = config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET = config("DYDX_API_PASSPHRASE_TESTNET")

#KEYS - Export. These variables will be exported to all of our functions
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PRODUCTION" else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY  = DYDX_API_KEY_MAINNET if MODE == "PRODUCTION" else DYDX_API_KEY_TESTNET
DYDX_API_SECRET  = DYDX_API_SECRET_MAINNET if MODE == "PRODUCTION" else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE  = DYDX_API_PASSPHRASE_MAINNET if MODE == "PRODUCTION" else DYDX_API_PASSPHRASE_TESTNET

#HOST - Export
HOST = API_HOST_MAINNET if MODE == "PRODUCTION" else API_HOST_SEPOLIA

#HTTP Provider (from Alchemy, go to the App DYDX Testnet Application that was setup before, view Key, copy HTTPS )
HTTP_PROVIDER_MAINNET = "https://eth-mainnet.g.alchemy.com/v2/_9wG0Fvylx0gL6i_CmbXLnES9E5wHvj5"
HTTP_PROVIDER_TESTNET = "https://eth-sepolia.g.alchemy.com/v2/9Reol1fzBwhW-UnEKrkKbGNdlv0k4Rq2"
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET if MODE == "PRODUCTION" else HTTP_PROVIDER_TESTNET
