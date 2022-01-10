# import PySimpleGUI as sgui
import os
import time
import datetime as dt

def inp_handle(type_to = ["d", "t", "n"]):
    if type_to == "d":
        try:
            str_input = input("Insira a data (ddmmaaaa):\n")
            tru_date = dt.date(
                year = int( str_input[4:] ), 
                month = int( str_input[2:4] ), 
                day = int( str_input[0:2] )
            )
            return tru_date
        except:
            print("Data inválida!\n\n")
            prompter()
    elif type_to == "t":
        try:
            str_input = input("Insira o horário (hhmmss):\n")
            tru_time = dt.time(
                second = int( str_input[4:] ),
                minute = int( str_input[2:4] ),
                hour = int( str_input[0:2] )
            )
            return tru_time
        except:
            print("Horário inválido!\n\n")
            prompter()
    elif type_to == "n":
        try:
            str_input = input("Insira o valor (0000.00):\n")
            return float( str_input )
        except:
            print("Valor inválido!\n\n")
            prompter()

def data_storage(array):
    """Save the array of inputs in a text file"""
    work_dir = os.getcwd() + "\\Cashd"
    os.chdir(work_dir)

    regfile = open("input_reg.csv", "a")
    for item in array:
        regfile.write(item)
    regfile.close()

def countdown_message(message, seconds = 10):
    while seconds > 0:
        print(message, seconds, end = "\r")
        time.sleep(1)
        seconds -= 1

def prompter():
    inp_date = inp_handle( type_to = "d" )
    inp_time = inp_handle( type_to = "t" )
    inp_value = inp_handle( type_to = "n" )
    try:
        data_storage(
            [str(inp_date)+",", str(inp_time)+",", str(inp_value), "\n"]
        )
        print("Dados armazenados!\n")
    except Exception as prompter_error:
        print(prompter_error)
        countdown_message("Falha no aramazenamento dos dados, fechando em", 5)
    finally:
        prompter()

prompter()