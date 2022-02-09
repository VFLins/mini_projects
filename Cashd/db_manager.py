import datetime as dt
import sqlalchemy as alch
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.ext.declarative import declarative_base
from time import sleep
from platform import system
from os import mkdir, chdir
from os.path import isdir, expanduser

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
   sleep_time = 30
   print("ERRO FATAL:\n", manage_dir_error, "\nFechando em 30 segundos...", sep="")
   sleep(30)
   quit()

if SYS_NAME == "Windows":
   DB_ENGINE = alch.create_engine("sqlite:///DB.sqlite")
else:
   DB_ENGINE = alch.create_engine("sqlite:////DB.sqlite")

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
DB_METADATA = alch.MetaData(bind = DB_ENGINE)

## Preparing for queries
def querry_all_entry():
   spacing = "{:>6}  {:<10}  {:<8}  {:>11}"

   try:
      cur_query = Query(tb_entry, session = DB_MSESSION).order_by(tb_entry.Id)
      if cur_query.count() == 0:
         print("Nada para mostrar aqui, tabela vazia!")
      else:
         print(spacing.format("Id", "Data", "Hora", "Valor"))
         for obs in cur_query:
            print(spacing.format(obs.Id, str(obs.Data), str(obs.Hora), obs.Valor))
   except Exception as querry_all_entry_error:
      print("Erro imprevisto ao ler todos os dados:", querry_all_entry_error, sep = "\n")

def querry_range_entry(init, end):
   spacing = "{:>6}  {:<10}  {:<8}  {:>11}"

   try:
      cur_query = Query(tb_entry, session = DB_MSESSION).order_by(tb_entry.Id).filter(tb_entry.Data.between(
         init, end
      ))
      if cur_query.count() == 0:
         print("Nenhum registro no intervalo especificado!")
      else:
         print(spacing.format("Id", "Data", "Hora", "Valor"))
         for obs in cur_query:
            print(spacing.format(obs.Id, str(obs.Data), str(obs.Hora), obs.Valor))

   except ValueError:
      print("A data inicial deve ser inferior ou igual à data final!")
   except Exception as querry_range_entry_error:
      print("Erro imprevisto ao ler todos os dados:", querry_range_entry_error, sep = "\n")

      
