from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits
from func_messaging import send_message


#MAIN FUNCTION
if __name__ == "__main__":

    #Message on start
    send_message("Bot launch successful")

    #Connect to client
    #If something goes wrong, exit and exit quickly and preferentially notify me that there was a problem
    try:
        print("Connecting to Client...")
        client = connect_dydx()
    except Exception as e:
        print(f"Error connecting to client: {e}")
        send_message("Failed to connect to client.")
        exit(1) #exit the code and kill the python script


    #Abort all open positions
    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders = abort_all_positions(client)
        except Exception as e:
            print(f"Error closing all positions: {e}")
            send_message(f"Error closing all positions. {e}")
            exit(1)  # exit the code and kill the python script


    #Find Cointegrated Pairs
    if FIND_COINTEGRATED:

        #Construct Market Prices
        try:
            print("Fetching market prices, please allow 3 mins...")
            df_market_prices = construct_market_prices(client)
        except Exception as e:
            print(f"Error constructing market prices: {e}")
            send_message(f"Error constructing market prices: {e}")
            exit(1)  # exit the code and kill the python script


        #Store Cointegrated Pairs (loop through all of our prices, find which pairs are co-integrated and store them)
        try:
            print("Storing cointegrated pairs...")
            stores_result = store_cointegration_results(df_market_prices)
            if stores_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1) #Exit the code; stop the script from running if there is nothing cointegrated

        except Exception as e:
            print(f"Error saving cointegrated pairs: {e}")
            send_message(f"Error saving cointegrated pairs: {e}")
            exit(1)

    #Run as always on (this will keep looping over and over)
    while True:

        #Place trades for opening positions
        if MANAGE_EXITS:
            try:
                print("Managing exits...")
                manage_trade_exits(client)
            except Exception as e:
                print(f"Error managing exiting positions: {e}")
                send_message(f"Error managing exiting positions: {e}")
                exit(1)

        #Place trades for opening positions
        if PLACE_TRADES:
            try:
                print("Finding trading opportunities...")
                open_positions(client)
            except Exception as e:
                print(f"Error trading pairs: {e}")
                send_message(f"Error opening trades {e}")
                exit(1)