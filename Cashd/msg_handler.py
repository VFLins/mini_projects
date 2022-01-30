import time
import datetime as dt
from db_manager import tb_entry, DB_MSESSION

SHORTCUTS = (
   ["HOJE", "AGORA"],
   ["Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido"]
)

def countdown_message(*message, seconds = 5):
   while seconds > 0:
      print(message, seconds, end = "\r", sep ="")
      time.sleep(1)
      seconds -= 1
   quit()

def inp_date_handle():
   str_input = input("Insira a data (ddmmaaaa):\n")
   try:
      if str_input.upper() in SHORTCUTS[0]:
         tru_date = shortcut_handle( str_input )
      else:
         tru_date = str(dt.date(
            year = int( str_input[4:] ), 
            month = int( str_input[2:4] ), 
            day = int( str_input[0:2] )
         )
      )
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
      if str_input.upper() in SHORTCUTS[0]:
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

def inp_float_handle():
   try:
      str_input = input("Insira o valor (0000.00):\n")
      return float( str_input )
   except:
      print("Valor inválido!\n\n")
      prompter()

def shortcut_handle(shortcut):
   if shortcut.upper() == SHORTCUTS[0][0]:
      output = str( dt.date.today() )
   elif shortcut.upper() == SHORTCUTS[0][1]:
      output = dt.datetime.now().strftime("%H:%M:%S")
   return output

def prompter():
   inp_date = inp_date_handle()
   inp_time = inp_time_handle()
   inp_value = inp_float_handle()
   try:
      entry = tb_entry(
         Data = inp_date,
         Hora = inp_time,
         Valor = inp_value
      )
      DB_MSESSION.add(entry)
      DB_MSESSION.commit()
      print("Dados armazenados!\n")
   except Exception as prompter_error:
      print(prompter_error)
      countdown_message("Falha no aramazenamento dos dados, fechando em")
   finally:
      prompter()
