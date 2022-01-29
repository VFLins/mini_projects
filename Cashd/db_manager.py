import os
from re import I
import msg_handler as mh
import sqlalchemy as alch
from sqlalchemy.orm import sessionmaker
import platform as pf

DB_DECBASE = alch.declarative_base()

def manage_dir():
   """
   Defines a working directory based on current OS for the the program to manage it's files
   """
   global WORK_DIR
   global SYS_NAME
   SYS_NAME = pf.system()
   try:
      if SYS_NAME == "Windows":
         WORK_DIR = os.path.expanduser("~") + "\\Appdata\\Roaming\\Cashd"
         if not os.path.isdir(WORK_DIR):
            os.mkdir(WORK_DIR)
      elif SYS_NAME == "Darwin":
         WORK_DIR = os.path.expanduser("~") + "\\Library\\\Preferences\\Cashd"
         if not os.path.isdir(WORK_DIR):
            os.mkdir(WORK_DIR)
      elif SYS_NAME =="Linux":
         WORK_DIR = os.path.expanduser("~") + "\\.local\\Share\\Cashd"
         if not os.path.isdir(WORK_DIR):
            os.mkdir(WORK_DIR)
      os.chdir(WORK_DIR)
   except Exception as manage_dir_error:
      print(manage_dir_error)
      mh.countdown_message("Não foi possível definir pasta de trabalho, fechando em")
manage_dir()

if SYS_NAME == "Windows":
   DB_ENGINE = alch.create_engine("sqlite:///" + WORK_DIR + "DB.sqlite")
else:
   DB_ENGINE = alch.create_engine("sqlite:////" + WORK_DIR + "DB.sqlite")

#DB_METADATA = alch.MetaData(bind = DB_ENGINE)

if not os.path.isfile(WORK_DIR + "DB.sqlite"): 
   DB_DECBASE.metadata.create_all(DB_ENGINE)

DB_SESSION = sessionmaker(bind = DB_ENGINE)

class tb_entry(DB_DECBASE):
   __tablename__ = "entry"
   Id = alch.Column(alch.Integer, primary_key = True)
   Data = alch.Column(alch.Date)
   Hora = alch.Column(alch.Time)
   Valor = alch.Column(alch.Float)


