#Handle any private connection functions such as opening and closing positions, etc. that we might have.

from datetime import datetime, timedelta
from func_utils import format_number
import time

from pprint import pprint


#Get existing open positions
def is_open_positions(client, market):

    #Protect API
    time.sleep(0.2)

    #Get positions
    all_positions = client.private.get_positions(market=market, status="OPEN")

    #Determine if open
    if len(all_positions.data["positions"]) > 0:
        return True #This means there must be open positions for that market
    else:
        return False

#Check order status; this function returns an order status by passing in the client and the order ID.
def check_order_status(client, order_id):
    order = client.private.get_order_by_id(order_id)
    #There might not be a status for an order if something potentially fails
    if order.data:
        if "order" in order.data.keys():
            return order.data["order"]["status"]
    return "FAILED"

#Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    # Get Position Id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]  # 1581

    # Get expiration time. Add a minute to the server time to give a valid expiration time to my order
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "+00:00")) + timedelta(seconds=70)

    # Place an order
    placed_order = client.private.create_order(
        position_id=position_id,  # required for creating the order signature
        market=market,
        side=side,  # "BUY" or "SELL"
        order_type="MARKET",
        post_only=False, #will be left as false since we only create market orders
        size=size,  # This is in BTC, not in USD (e.g. 0.001)
        price=price, #worst acceptable price
        # This is the worst price (if I buy I want the price to be above today's market price; selling: Below)
        limit_fee='0.015',
        expiration_epoch_seconds=expiration.timestamp(),
        time_in_force="FOK",
        reduce_only=reduce_only
        # By changing this from False (which we used for buying) to True (if we sell) it knew to close the existing open position.
    )

    # print(placed_order.data)

    # Return result
    return placed_order.data


#Abort all open positions
def abort_all_positions(client):

    #Cancel all orders
    client.private.cancel_all_orders()

    #Protect API.
    time.sleep(0.5)

    #Get markets for reference of tick size
    markets = client.public.get_markets().data #market data of different markets incl. tickSize since I need the right decimals for size and price.

    #Protect API.
    time.sleep(0.5)

    #Get all open positions from dydx
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"] # e.g.: [{'market': 'CRV-USD', 'status': 'OPEN', 'side': 'SHORT', 'size': '-100', 'maxSize': '-100', 'entryPrice': '0.648000', 'exitPrice': '0.000000', 'unrealizedPnl': '-0.070000', 'realizedPnl': '0.000000', 'createdAt': '2024-03-18T20:11:32.499Z', 'closedAt': None, 'sumOpen': '100', 'sumClose': '0', 'netFunding': '0'}, {'market': 'SOL-USD', 'status': 'OPEN', 'side': 'LONG', 'size': '1', 'maxSize': '1', 'entryPrice': '199.412000', 'exitPrice': '0.000000', 'unrealizedPnl': '1.674950', 'realizedPnl': '-0.017347', 'createdAt': '2024-03-18T19:53:43.414Z', 'closedAt': None, 'sumOpen': '1', 'sumClose': '0', 'netFunding': '-0.017347'}, {'market': 'ETH-USD', 'status': 'OPEN', 'side': 'LONG', 'size': '0.01', 'maxSize': '0.01', 'entryPrice': '3489.700000', 'exitPrice': '0.000000', 'unrealizedPnl': '0.073000', 'realizedPnl': '-0.000363', 'createdAt': '2024-03-18T19:52:38.212Z', 'closedAt': None, 'sumOpen': '0.01', 'sumClose': '0', 'netFunding': '-0.000363'}, {'market': 'BTC-USD', 'status': 'OPEN', 'side': 'LONG', 'size': '0.001', 'maxSize': '0.001', 'entryPrice': '67156.000000', 'exitPrice': '0.000000', 'unrealizedPnl': '-0.043970', 'realizedPnl': '-0.000217', 'createdAt': '2024-03-18T19:50:35.967Z', 'closedAt': None, 'sumOpen': '0.001', 'sumClose': '0', 'netFunding': '-0.000217'}]
    # pprint(positions)

    #Handle open positions
    close_orders = []
    if len(all_positions) > 0:

        #Loop through each positions
        for position in all_positions:

            #Determine Market
            market = position["market"] #BTC-USD e.g.

            #Determine Side
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"

            #Get Price
            price = float(position["entryPrice"])
            #For simplicity reasons I am happy to close this out if it is 70% worse than it was when I opened the position, because I am not expecting to be in positions very long and I am not expecting the prices to move that wildly
            #Alternative: Pull current price from dydx and say make it 5% worse than the current price
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            #format price in a way that it is the exact right size, decimals etc. for dydx to go and accept it as an order.
            accept_price = format_number(accept_price, tick_size)

            #Place order to close
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"], #size = quantity that we have right now open on that order
                accept_price,
                True
            )

            #Append the result
            close_orders.append(order)

            #Protect API
            time.sleep(0.2)

        #Return closed orders
        return close_orders