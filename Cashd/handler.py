import datetime as dt
from collections import OrderedDict
import prompter as ppt
from time import sleep

SHORTCUTS = (
   OrderedDict( {
      "HOJE" : "date", 
      "AGORA" : "time", 
      "CONS" : "call", 
      "REM" : "call"} ),
   ["Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido",
   "Cancela a entrada atual de dados e entra no modo de consluta",
   "Cancela a entrada atual de dados e entra no modo de remoção"]
)

def countdown_message(message, error, seconds = 15):
   print("\n", message, error, end = "\n", sep = "\n")
   while seconds > 0:
      PSECONDS = "{:0>2d}".format(seconds)
      print("Fechando em ...", PSECONDS, end = "\r", sep = "")
      sleep(1)
      seconds -= 1
   quit()

def inp_date_handle() -> dt.date:
   """
   Returns input from the user as a datetime.date object.
   """
   def is_date_type(x) -> bool:
      try: return isinstance( x, type(dt.date.today()) )
      except: return False
       
   try:
      str_input = input("Insira a data (ddmmaaaa): ")
      inp_is_date = is_date_type(str_input)
      while not inp_is_date:
         if str_input.upper() in SHORTCUTS[0][0::3]:
            tru_date = shortcut_handle( str_input )
            inp_is_date = is_date_type(tru_date)
         else:
            try:
               tru_date = dt.date(
                  year = int( str_input[4:] ), 
                  month = int( str_input[2:4] ), 
                  day = int( str_input[0:2] )
               )
               inp_is_date = is_date_type(tru_date)
            except:
               print("Valor obtido para data é inválido!")
               str_input = input("Insira a data (ddmmaaaa): ")
      return tru_date
   except Exception as ERROR:
      countdown_message("ERRO AO ATRIBUIR DATA:", error = ERROR)

def inp_time_handle() -> dt.time:
   """
   Returns input from the user as datetime.time object.
   """
   def is_time_type(x) -> bool:
      try: return isinstance( x, type(dt.datetime.now().time()) )
      except: return False

   try:
      str_input = input("Insira o horário (hhmmss): ")
      inp_is_time = is_time_type(str_input)
      while not inp_is_time:
         if str_input.upper() in SHORTCUTS[0][1:]:
            tru_time = shortcut_handle( str_input )
            inp_is_time = is_time_type(tru_time)
         else:
            try:
               tru_time = dt.time(
                  second = int( str_input[4:] ),
                  minute = int( str_input[2:4] ),
                  hour = int( str_input[0:2] )
               )
               inp_is_time = is_time_type(tru_time)
            except:
               print("Valor obtido para hora é inválido!")
               str_input = input("Insira o horário (hhmmss): ")
      return tru_time
   except Exception as ERROR:
      countdown_message("ERRO AO ATRIBUIR HORÁRIO:", error = ERROR)

def inp_float_handle() -> float:
   """
   Returns input from the user as float object.
   """
   def is_numeric_type(x) -> bool:
      try:
         if isinstance(x, bool): return False
         else: return isinstance(x, (int, float))
      except:
         return False

   try:
      str_input = input("Insira o valor (0000.00): ")
      inp_is_numeric = is_numeric_type(str_input)
      while not inp_is_numeric:
         if str_input.upper() in SHORTCUTS[0][2]:
            tru_numeric = shortcut_handle( str_input )
            inp_is_numeric = is_numeric_type(tru_numeric)
         else: 
            try: 
               tru_numeric = float( str_input )
               inp_is_numeric = is_numeric_type(tru_numeric)
            except:
               print("Valor inválido! Separe apenas decimais com ponto.")
               str_input = input("Insira o valor (0000.00): ")
      return tru_numeric
   except Exception as ERROR:
      countdown_message("ERRO AO ATRIBUIR VALOR:", error = ERROR)

def shortcut_handle(shortcut, type = "call"):

   def keys_by_value(dict, value):
    KEYS_LIST = list()
    ITEMS_LIST = dict.items()
    for item  in ITEMS_LIST:
        if item[1] == value:
            KEYS_LIST.append(item[0])
    return  KEYS_LIST

   # Shortcut inserted must be of the type informed and call
   SEL_SHORTCUTS = keys_by_value(SHORTCUTS[0], "call")
   if  type != "call":
      SEL_SHORTCUTS.append( keys_by_value(SHORTCUTS[0], type) )

   if shortcut.upper() == "HOJE":
      output = dt.date.today()
      return output
   elif shortcut.upper() == "AGORA":
      output = dt.datetime.now().time()
      return output
   elif shortcut.upper() == "CONS":
      ppt.prompt_consult()
   elif shortcut.upper() == "REM":
      ppt.prompt_deletion()
