import sqlalchemy as alch
from sqlalchemy.orm import sessionmaker
from msg_handler import countdown_message
from platform import system
from os import mkdir, chdir
from os.path import isdir, isfile, expanduser

DB_DECBASE = alch.declarative_base()

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
   countdown_message("Não foi possível definir pasta de trabalho, fechando em")

if SYS_NAME == "Windows":
   DB_ENGINE = alch.create_engine("sqlite:///DB.sqlite")
else:
   DB_ENGINE = alch.create_engine("sqlite:////DB.sqlite")

#DB_METADATA = alch.MetaData(bind = DB_ENGINE)

if not isfile(WORK_DIR + "DB.sqlite"): DB_DECBASE.metadata.create_all(DB_ENGINE)

DB_SESSION = sessionmaker(bind = DB_ENGINE)
DB_MSESSION = DB_SESSION()

class tb_entry(DB_DECBASE):
   __tablename__ = "entry"
   Id = alch.Column(alch.Integer, primary_key = True)
   Data = alch.Column(alch.Date)
   Hora = alch.Column(alch.Time)
   Valor = alch.Column(alch.Float)

print("SYS_NAME: ", SYS_NAME, ", WORK_DIR: ", WORK_DIR, ", ", ", DB_ENGINE: ", DB_ENGINE, ", DB_SESSION: ", DB_SESSION, "DB_MSESSION: ", DB_MSESSION)
input("is it ok?")
