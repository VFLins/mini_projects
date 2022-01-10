# import PySimpleGUI as sgui
import os
import time
import datetime as dt
import numpy as np

def date_handle(str_date):
    """Converts the ddmmaaaa string input to actual date format"""
    try:
        tru_date = dt.date(
            year = int( str_date[4:] ), 
            month = int( str_date[2:4] ), 
            day = int( str_date[0:2] )
        )
        return tru_date
    except:
        print("Data inválida!\n\n")
        prompter()

def time_handle(str_time):
    """Converts the hhmmss string input to actual time format"""
    try:
        tru_time = dt.time(
            second = int( str_time[4:] ),
            minute = int( str_time[2:4] ),
            hour = int( str_time[0:2] )
        )
        return tru_time
    except:
        print("Horário inválido!\n\n")
        prompter()

def data_storage(array):
    """Save the array of inputs in a text file"""
    work_dir = "C:\\Users\\vflin\OneDrive\\Documentos\\GitHub\\Projects\\Cashd"
    os.chdir(work_dir)

    regfile = open("input_reg.txt", "a")
    for item in array:
        np.savetxt(regfile, item)
    regfile.close()

def countdown_message(message, seconds = 10):
    while seconds > 0:
        print(message, seconds, end = "\r")
        time.sleep(1)
        seconds -= 1

def prompter():
    inp_date = date_handle( input("Insira a data (ddmmaaaa):\n") )
    inp_time = time_handle( input("Insira o horário (hhmmss):\n"))
    inp_value = float( input("Insira o valor (0000.00):\n") )
    try:
        data_storage(
            [str(inp_date), str(inp_time), str(inp_value)]
        )
        print("Armazenando dados...")
        time.sleep(3)
    except Exception as prompter_error:
        print(prompter_error)
        countdown_message("Falha no aramazenamento dos dados, fechando em", 3)

prompter()