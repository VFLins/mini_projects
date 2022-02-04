import err_handler as eh
import sqlalchemy as alch
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, date
from sqlalchemy.ext.declarative import declarative_base
from platform import system
from os import mkdir, chdir
from os.path import isdir, isfile, expanduser

DB_DECBASE = declarative_base()

SYS_NAME = system()
try:
   if SYS_NAME == "Windows":
      WORK_DIR = expanduser("~") + "\\Appdata\\Roaming\\Cashd"
      if not isdir(WORK_DIR): mkdir(WORK_DIR)
   elif SYS_NAME == "Darwin":
      WORK_DIR = expanduser("~") + "\\Library\\\Preferences\\Cashd"
      if not isdir(WORK_DIR): mkdir(WORK_DIR)
   elif SYS_NAME =="Linux":
      WORK_DIR = expanduser("~") + "\\.local\\Share\\Cashd"
      if not isdir(WORK_DIR): mkdir(WORK_DIR)
   chdir(WORK_DIR)
except Exception as manage_dir_error:
   print(manage_dir_error)
   eh.countdown_message("Não foi possível definir pasta de trabalho, fechando em")

if SYS_NAME == "Windows":
   DB_ENGINE = alch.create_engine("sqlite:///DB.sqlite")
else:
   DB_ENGINE = alch.create_engine("sqlite:////DB.sqlite")

#DB_METADATA = alch.MetaData(bind = DB_ENGINE)

DB_SESSION = sessionmaker(bind = DB_ENGINE)
DB_MSESSION = DB_SESSION()

class tb_entry(DB_DECBASE):
   __tablename__ = "entry"
   Id = alch.Column(alch.Integer, primary_key = True)
   Data = alch.Column(alch.Date)
   Hora = alch.Column(alch.Time)
   Valor = alch.Column(alch.Float)

   def __repr__(self):
      return "<entry(Data={}, Hora={}, Valor={})>".format(
         self.Data, self.Hora, self.Valor
      )

DB_DECBASE.metadata.create_all(DB_ENGINE)

def consult_database():
   sel_mode = input("Ver tudo/Selecionar por data [t/d]: ")
   try:
      if sel_mode.upper() == "T":
         this_querry = DB_MSESSION.querry(tb_entry)
         for obs in this_querry.order_by(tb_entry.Id):
            print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
      elif sel_mode.upper() == "D":
         init_date = input("Informe a data inicial [ddmmaaaa]: ")
         end_date = input("Informe a data final [ddmmaaaa]: ")
         range_date = [init_date + timedelta(days=x) for x in range(0, (end_date-init_date).days)]

         this_querry = DB_MSESSION.querry(tb_entry).filter_by(Data =range_date)
         for obs in this_querry.order_by(tb_entry.Id):
            print("{:<5} {:>11} {:<10} {:<21}").format(obs.Id, obs.Data, obs.Hora, obs.Valor)
   except:
      eh.countdown_message("Não foi possível ler dados, fechando em...")
