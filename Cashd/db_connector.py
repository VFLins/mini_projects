import os
import time
import sqlite3
import platform as pf

def manage_dir():
   """
   Defines a working directory based on current OS for the the program to manage it's files
   """
   global work_dir
   try:
      if pf.system() == "Windows":
         work_dir = os.path.expanduser("~") + "\\Appdata\\Roaming\\Cashd"
         if not os.path.isdir(work_dir):
            os.mkdir(work_dir)
      elif pf.system() == "Darwin":
         work_dir = os.path.expanduser("~") + "\\Library\\\Preferences\\Cashd"
         if not os.path.isdir(work_dir):
            os.mkdir(work_dir)
      elif pf.system() =="Linux":
         work_dir = os.path.expanduser("~") + "\\Cashd"
         if not os.path.isdir(work_dir):
            os.mkdir(work_dir)
      os.chdir(work_dir)
   except Exception as manage_dir_error:
      print(manage_dir_error)
      countdown_message("Não foi possível definir pasta de trabalho, fechando em")

def db_connection(db_name):
   """
    :param db_name: String with database's file name
    :return: Connection object
   """
   try:
         conn = sqlite3.Connection(dbpath + "\\" + db_name)
         print("Conectado com a base de dados!")
   except Exception as err:
      main.countdown_message(err, "\nFechando em ...")
   finally:
      if conn:
         conn.close()

def db_table_builder(table_name, schema):
   """
   :table_name: String with name of the table
   :schema: 
   """

manage_dir()
if os.path.isdir(dbpath):
   dbpath = work_dir + "\\database"
else:
   os.mkdir(dbpath)
   dbpath = work_dir + "\\database"

