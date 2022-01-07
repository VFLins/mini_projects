# import PySimpleGUI as sgui
import datetime as dt
import fbd

if isfile(/database/db.fdb)

def date_handle(str_date):
    tru_date = dt.date(
        int( str_date[4:] ), 
        int( str_date[2:4] ), 
        int( str_date[0:2] )
    )
    return tru_date

def prompter():
    inp_date = date_handle( input("Insira a data (ddmmaaaa): \n") )
    inp_value = input("Insira o valor (0000.00): \n")

prompter()