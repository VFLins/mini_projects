import db_manager as dm
import datetime as dt
import handler as hdl


def prompt_entry():
   print("\nMODO INSERÇÃO:")
   inp_date = hdl.inp_date_handle()
   inp_time = hdl.inp_time_handle()
   inp_value = hdl.inp_float_handle()
   try:
      entry = dm.tb_entry(Data = inp_date, Hora = inp_time, Valor = inp_value)
      dm.DB_MSESSION.add(entry)
      dm.DB_MSESSION.commit()
      print("Dados armazenados!\n")
   except Exception as entry_prompter_error:
      print(entry_prompter_error)
      hdl.countdown_message("Falha no aramazenamento dos dados, fechando em")
   finally:
      prompt_entry()

def prompt_consult():
   print("\nMODO CONSULTA:")

   has_run = False
   try:
      sel_mode = input("Ver tudo/Selecionar por data/Cancelar [t/d/c]: ")
      while not has_run:

         if sel_mode.upper() == "T":
            this_querry = dm.DB_MSESSION.querry(dm.tb_entry)
            print(type(this_querry))
         
         elif sel_mode.upper() == "D":
            init_date = input("Informe a data inicial [ddmmaaaa]: ")
            end_date = input("Informe a data final [ddmmaaaa]: ")
            range_date = [init_date + dt.timedelta(days=x) for x in range(0, (end_date-init_date).days)]
            this_querry = dm.DB_MSESSION.querry(dm.tb_entry).filter_by(Data =range_date)
            for obs in this_querry.order_by(dm.tb_entry.Id):
               print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
            has_run = True

         elif sel_mode.upper() == "C":
            has_run = True
            print("\nMODO INSERÇÃO:")

         else:
            print("Método inválido! Selecione algum dos métodos disponíveis.")
            sel_mode = input("Ver tudo/Selecionar por data/Cancelar [t/d/c]: ")
   except:
      hdl.countdown_message("Não foi possível ler dados, fechando em...")
   finally:
      prompt_entry()

def prompt_deletion():
   print("\nMODO REMOÇÃO:")
   return
