import os
import time
import sqlite3
import platform as pf

def manage_dir():
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
      time.sleep(10)

manage_dir()
dbpath = work_dir + "\\database"

def db_connection(db_name):
   conn = None
   try:
      if os.path.isdir(dbpath):
         conn = sqlite3.Connection(dbpath + "\\" + db_name)
         print("Conectado com a base de dados!")
      else:
         os.mkdir(dbpath)
         conn = sqlite3.Connection(dbpath + "\\" + db_name)
         print("Conectado com a base de dados!")
   except Exception as err:
      main.countdown_message(err, "\nFechando em ...")

db_connection()

