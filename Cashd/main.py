# import PySimpleGUI as sgui
import os
import time
import db_connector
import platform as pf
import datetime as dt

shortcut_list = ["HOJE", "AGORA"]
shortcut_desc = [
   "Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido"
]

def shortcut_handle(shortcut):
   if shortcut.upper() == shortcut_list[0]:
      output = str( dt.date.today() )
   elif shortcut.upper() == shortcut_list[1]:
      output = dt.datetime.now().strftime("%H:%M:%S")
   return output

def inp_date_handle():
   str_input = input("Insira a data (ddmmaaaa):\n")
   try:
      if str_input.upper() in shortcut_list:
         tru_date = shortcut_handle( str_input )
      else:
         tru_date = str(dt.date(
            year = int( str_input[4:] ), 
            month = int( str_input[2:4] ), 
            day = int( str_input[0:2] )
         ))
      if bool(dt.datetime.strptime(tru_date, "%Y-%m-%d")):
         return tru_date
      else:
         raise ValueError
   except ValueError:
      print("Valor obtido para data é inválido!")
      prompter()
   except Exception as error:
      countdown_message("Erro não previsto:\n", error + "\n", "Fechando em ")

def inp_time_handle():
   str_input = input("Insira o horário (hhmmss):\n")
   try:
      if str_input.upper() in shortcut_list:
         tru_time = shortcut_handle( str_input )
      else:
         tru_time = dt.time(
            second = int( str_input[4:] ),
            minute = int( str_input[2:4] ),
            hour = int( str_input[0:2] )
         )
      if bool(dt.datetime.strptime(tru_time, "%H:%M:%S")):
         return tru_time
      else:
         raise ValueError()
   except ValueError:
      print("Valor obtido para hora é inválido!")
      prompter()
   except Exception as error:
      countdown_message("Erro não previsto:\n", error + "\n", "Fechando em ")

def inp_numeric_handle():
   try:
      str_input = input("Insira o valor (0000.00):\n")
      return float( str_input )
   except:
      print("Valor inválido!\n\n")
      prompter()

def data_storage(array):
   """Save the array of inputs in a text file"""
   db_connector.manage_dir()
   regfile = open("input_reg.csv", "a")
   for item in array:
      regfile.write(item)
   regfile.close()

def countdown_message(*message, seconds = 5):
   while seconds > 0:
      print(message, seconds, end = "\r", sep ="")
      time.sleep(1)
      seconds -= 1
   quit()

def prompter():
   inp_date = inp_date_handle()
   inp_time = inp_time_handle()
   inp_value = inp_numeric_handle()
   try:
      data_storage(
         [str(inp_date)+",", str(inp_time)+",", str(inp_value), "\n"]
      )
      print("Dados armazenados!\n")
   except Exception as prompter_error:
      print(prompter_error)
      countdown_message("Falha no aramazenamento dos dados, fechando em")
   finally:
      prompter()

db_connector.manage_dir()
print(
   "Bem vindo ao Cashd, seus dados serão salvos em: ",
   work_dir + "\\input_reg.csv\n\n",
   "ATALHOS:",
   sep = ""
)
[print(shortcut_list[ind] + ": ", shortcut_desc[ind]) for ind in range(len(shortcut_list))]
print("")
prompter()