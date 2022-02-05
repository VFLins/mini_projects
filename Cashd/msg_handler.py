import datetime as dt
from logging import exception
from time import sleep

SHORTCUTS = (
   ["HOJE", "AGORA", "CONS"],
   ["Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido",
   "Cancela a entrada atual de dados e entra no modo de consluta"]
)

def countdown_message(*message, seconds = 10):
   while seconds > 0:
      print(message, seconds, end = "\r", sep ="")
      sleep(1)
      seconds -= 1
   quit()

def inp_date_handle() -> dt.date:
   """
   Returns input from the user as a datetime.date object.
   """
   def is_date_type(x) -> bool:
      return isinstance( x, type(dt.date.today()) )
       
   try:
      str_input = input("Insira a data (ddmmaaaa): ")
      while not is_date_type(str_input):
         if str_input.upper() in SHORTCUTS[0][0::2]:
            tru_date = shortcut_handle( str_input )
         else:
            try:
               tru_date = dt.date(
                  year = int( str_input[4:] ), 
                  month = int( str_input[2:4] ), 
                  day = int( str_input[0:2] )
               )
            except:
               print("Valor obtido para data é inválido!")
               str_input = input("Insira a data (ddmmaaaa): ")
      return tru_date
   except Exception as error:
      countdown_message("Erro não previsto ao lidar com a data:\n", error, "\nFechando em ")

def inp_time_handle() -> dt.time:
   """
   Returns input from the user as datetime.time object.
   """
   def is_time_type(x) -> bool:
      return isinstance( x, type(dt.datetime.now().time()) )

   try:
      str_input = input("Insira o horário (hhmmss): ")
      while not is_time_type(str_input):
         if str_input.upper() in SHORTCUTS[0][1:]:
            tru_time = shortcut_handle( str_input )
         else:
            try:
               tru_time = dt.time(
                  second = int( str_input[4:] ),
                  minute = int( str_input[2:4] ),
                  hour = int( str_input[0:2] )
               )
            except:
               print("Valor obtido para hora é inválido!")
               str_input = input("Insira o horário (hhmmss): ")
      return tru_time
   except Exception as error:
      countdown_message("Erro não previsto ao definir horário:\n", error, "\nFechando em ")

def inp_float_handle() -> float:
   """
   Returns input from the user as float object.
   """
   def is_numeric_type(x) -> bool:
      if isinstance(x, bool): return False
      else: return isinstance(x, (int, float))

   try:
      str_input = input("Insira o valor (0000.00): ")
      while not is_numeric_type(str_input):
         if str_input.upper() in SHORTCUTS[0][2]:
            shortcut_handle( str_input )
         else: 
            try: 
               tru_numeric = float( str_input )
            except:
               print("Valor inválido! Separe apenas decimais com ponto.")
               str_input = input("Insira o valor (0000.00): ")
      return tru_numeric
   except Exception as error:
      countdown_message("Erro não previsto ao definir valor:\n", error, "\nFechando em ")

def shortcut_handle(shortcut):
   if shortcut.upper() == SHORTCUTS[0][0]:
      output = dt.date.today()
      return output
   elif shortcut.upper() == SHORTCUTS[0][1]:
      output = dt.datetime.now().time()
      return output
   elif shortcut.upper() == SHORTCUTS[0][2]:
      consult_database()
      prompter()
