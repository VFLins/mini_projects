import os
import time
import fdb
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
dbpath = work_dir + "\\mydb.fdb"

def db_connection():
   try:
      con = fdb.create_database(user = 'admin', password = 'serious_password',
      dsn = dbpath, page_size = 8000
      )
      print('Base de dados criada em', '\Cashd\database\mydb.fdb', '\n')
   except Exception as err:
      print(err)

db_connection()

