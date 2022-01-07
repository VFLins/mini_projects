import datetime as dt

def date_handle():
    str_date = "31122000"
    tru_date = dt.date(
        int( str_date[4:] ), 
        int( str_date[2:4] ), 
        int( str_date[0:2] )
    )
    print("true date is:", tru_date, "is that right?")

date_handle()