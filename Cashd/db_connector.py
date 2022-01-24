import os
import msg_handler as mh
import sqlite3
import sqlalchemy
import platform as pf

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
         WORK_DIR = os.path.expanduser("~") + "\\Cashd"
         if not os.path.isdir(WORK_DIR):
            os.mkdir(WORK_DIR)
      os.chdir(WORK_DIR)
   except Exception as manage_dir_error:
      print(manage_dir_error)
      mh.countdown_message("Não foi possível definir pasta de trabalho, fechando em")

manage_dir()
if SYS_NAME == "Windows":
   DB_ENGINE = sqlalchemy.create_engine("sqlite:///" + WORK_DIR + "DB.sqlite")
else:
   DB_ENGINE = sqlalchemy.create_engine("sqlite:////" + WORK_DIR + "DB.sqlite")
   
#def db_connection(db_name):
#   """
#    :param db_name: String with database's file name
#    :return: Connection object
#   """
#   global dbpath
#   dbpath = workdir + "\\database"
#   try:
#         conn = sqlite3.Connection(dbpath + "\\" + db_name)
#         print("Conectado com a base de dados!")
#   except Exception as err:
#      mh.countdown_message(err, "\nFechando em ...")
#   finally:
#      if conn:
#         conn.close()

#def db_table_builder(table_name, schema):
#   """
#   :table_name: String with name of the table
#   :schema: 
#   """

#if os.path.isdir(dbpath):
#   dbpath = WORK_DIR + "\\database"
#else:
#   os.mkdir(dbpath)
#   dbpath = WORK_DIR + "\\database"
