from datetime import datetime, timedelta


#Format number
#give our current number an example of what we wanted to match to in terms of decimals. The function will return a correctly formatted string for the price.
def format_number(curr_num, match_num):

    """
    Give current number an example of number with decimals desired
    Function will return the correctly formatted string
    """

    curr_num_string = f"{curr_num}"
    match_num_string = f"{match_num}"

    #If e.g. curr_num has 5 decimals and match_num only has 3 decimals, this is going to format our numbers so that it is matching our current number with the amount of decimals that we are requesting it to have here.
    if "." in match_num_string:
        match_decimals = len(match_num_string.split(".")[1])
        curr_num_string = f"{curr_num:.{match_decimals}f}"
        curr_num_string = curr_num_string[:]
        return curr_num_string
    else:
        return f"{int(curr_num)}"


#Stage 2:
#Format time
def format_time(timestamp):
    return timestamp.replace(microsecond=0).isoformat() #return timestamp replacing the microseconds and will return it in an ISO format which is what is needed for the dydx API

# Get ISO Times
def get_ISO_times():

    #Get timestamps. We use the strategy with hourly data and we get the date now and the date 100 hours before that (because that gives me the max. limit of 100 candles, see https://dydxprotocol.github.io/v3-teacher/#get-candles-for-market
    #See also fromISO and toISO, Then having these 100 candles I want another 100 candles etc. Define different timestamps in 100 hours slots and combine those together
    #This gives us 400 hours worth of close data (about 16 days worth of hourly data). Gives me enough historical data to work with
    date_start_0 = datetime.now()
    date_start_1 = date_start_0 - timedelta(hours=100)
    date_start_2 = date_start_1 - timedelta(hours=100)
    date_start_3 = date_start_2 - timedelta(hours=100)
    date_start_4 = date_start_3 - timedelta(hours=100)

    #Format datetimes
    times_dict = {
        "range_1": {
            "from_iso": format_time(date_start_1),
            "to_iso": format_time(date_start_0),
        },
        "range_2": {
            "from_iso": format_time(date_start_2),
            "to_iso": format_time(date_start_1),
        },
        "range_3": {
            "from_iso": format_time(date_start_3),
            "to_iso": format_time(date_start_2),
        },
        "range_4": {
            "from_iso": format_time(date_start_4),
            "to_iso": format_time(date_start_3),
        },

    }

    #Return results
    return times_dict

