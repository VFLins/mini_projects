# import PySimpleGUI as sgui
import datetime as dt
import os
import numpy as np

def date_handle(str_date):
    """Converts the ddmmaaaa string input to actual date format"""
    tru_date = dt.date(
        year = int( str_date[4:] ), 
        month = int( str_date[2:4] ), 
        day = int( str_date[0:2] )
    )
    return tru_date

def time_handle(str_time):
    """Converts the hhmmss string input to actual time format"""
    tru_time = dt.time(
        second = int( str_time[4:] ),
        minute = int( str_time[2:4] ),
        hour = int( str_time[0:2] )
    )
    return tru_time

def data_storage(array):
    """Save the array of inputs in a text file"""
    db_dir = "/database/cf.npy"
    if not path.isdir(db_dir):
        path.createdir(db_dir)
    np.savetxt(db_dir, array, delimiter=",", newline=":")

def prompter():
    inp_date = date_handle( input("Insira a data (ddmmaaaa):\n") )
    inp_time = time_handle( input("Insira o horário (hhmmss):\n"))
    inp_value = float( input("Insira o valor (0000.00):\n") )

    data_storage([inp_date, inp_time, inp_value])

prompter()