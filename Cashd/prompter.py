import msg_handler as mh
import db_manager as dm
from datetime import timedelta, date

def prompter():
   inp_date = mh.inp_date_handle()
   inp_time = mh.inp_time_handle()
   inp_value = mh.inp_float_handle()
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
   sel_mode = input("Ver tudo/Selecionar por data [t/d]: ")
   try:
      if sel_mode.upper() == "T":
         this_querry = dm.DB_MSESSION.querry(dm.tb_entry)
         for obs in this_querry.order_by(dm.tb_entry.Id):
            print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
      elif sel_mode.upper() == "D":
         init_date = input("Informe a data inicial [ddmmaaaa]: ")
         end_date = input("Informe a data final [ddmmaaaa]: ")
         range_date = [init_date + timedelta(days=x) for x in range(0, (end_date-init_date).days)]

         this_querry = dm.DB_MSESSION.querry(dm.tb_entry).filter_by(Data =range_date)
         for obs in this_querry.order_by(dm.tb_entry.Id):
            print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
   except:
      mh.countdown_message("Não foi possível ler dados, fechando em...")