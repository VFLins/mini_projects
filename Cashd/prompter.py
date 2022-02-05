import db_manager as dm
import datetime as dt
from time import sleep

SHORTCUTS = (
   ["HOJE", "AGORA", "CONS"],
   ["Retorna a data atual em um campo válido",
   "Retorna o horário atual em um campo válido",
   "Cancela a entrada atual de dados e entra no modo de consluta"]
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
         if str_input.upper() in SHORTCUTS[0][0::2]:
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

def shortcut_handle(shortcut):
   if shortcut.upper() == SHORTCUTS[0][0]:
      output = dt.date.today()
      return output
   elif shortcut.upper() == SHORTCUTS[0][1]:
      output = dt.datetime.now().time()
      return output
   elif shortcut.upper() == SHORTCUTS[0][2]:
      consult_database()
      
def prompter():
   inp_date = inp_date_handle()
   inp_time = inp_time_handle()
   inp_value = inp_float_handle()
   try:
      entry = dm.tb_entry(Data = inp_date, Hora = inp_time, Valor = inp_value)
      dm.DB_MSESSION.add(entry)
      dm.DB_MSESSION.commit()
      print("Dados armazenados!\n")
   except Exception as prompter_error:
      print(prompter_error)
      mh.countdown_message("Falha no aramazenamento dos dados, fechando em")
   finally:
      prompter()

def consult_database():
   has_run = False

   try:
      sel_mode = input("Ver tudo/Selecionar por data/Cancelar [t/d/c]: ")
      while not has_run:

         if sel_mode.upper() == "T":
            this_querry = dm.DB_MSESSION.querry(dm.tb_entry)
            for obs in this_querry.order_by(dm.tb_entry.Id):
               print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
            has_run = True
         
         elif sel_mode.upper() == "D":
            init_date = input("Informe a data inicial [ddmmaaaa]: ")
            end_date = input("Informe a data final [ddmmaaaa]: ")
            range_date = [init_date + timedelta(days=x) for x in range(0, (end_date-init_date).days)]
            this_querry = dm.DB_MSESSION.querry(dm.tb_entry).filter_by(Data =range_date)
            for obs in this_querry.order_by(dm.tb_entry.Id):
               print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
            has_run = True

         elif sel_mode.upper() == "C":
            has_run = True

         else:
            print("Método inválido! Selecione algum dos métodos disponíveis.")
            sel_mode = input("Ver tudo/Selecionar por data/Cancelar [t/d/c]: ")
   except:
      mh.countdown_message("Não foi possível ler dados, fechando em...")
   finally:
      prompter()
