import datetime as dt
import err_handler as eh
from db_manager import tb_entry, DB_MSESSION

SHORTCUTS = (
   ["HOJE", "AGORA"],
   ["Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido"]
)

def inp_date_handle():
   """
   Returns input from the user as datetime.date() object.
   """
   str_input = input("Insira a data (ddmmaaaa): ")
   try:
      if str_input.upper() in SHORTCUTS[0]:
         tru_date = shortcut_handle( str_input )
      else:
         tru_date = dt.date(
            year = int( str_input[4:] ), 
            month = int( str_input[2:4] ), 
            day = int( str_input[0:2] )
         )
      return tru_date
   except ValueError:
      print("Valor obtido para data é inválido!")
      prompter()
   except Exception as error:
      eh.countdown_message("Erro não previsto:\n", error + "\n", "Fechando em ")

def inp_time_handle():
   """
   Returns input from the user as datetime.time( ) object.
   """
   str_input = input("Insira o horário (hhmmss): ")
   try:
      if str_input.upper() in SHORTCUTS[0]:
         tru_time = shortcut_handle( str_input )
      else:
         tru_time = dt.time(
            second = int( str_input[4:] ),
            minute = int( str_input[2:4] ),
            hour = int( str_input[0:2] )
         )
      return tru_time
   except ValueError:
      print("Valor obtido para hora é inválido!")
      prompter()
   except Exception as error:
      eh.countdown_message("Erro não previsto:\n", error + "\n", "Fechando em ")

def inp_float_handle():
   try:
      str_input = input("Insira o valor (0000.00): ")
      return float( str_input )
   except:
      print("Valor inválido!\n\n")
      prompter()

def shortcut_handle(shortcut):
   if shortcut.upper() == SHORTCUTS[0][0]:
      output = dt.date.today()
   elif shortcut.upper() == SHORTCUTS[0][1]:
      output = dt.datetime.now().time()
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
      eh.countdown_message("Falha no aramazenamento dos dados, fechando em")
   finally:
      prompter()
