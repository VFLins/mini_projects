# import PySimpleGUI as sgui
import msg_handler as mh
import db_connector
import datetime as dt

def data_storage(array):
   """Save the array of inputs in a text file"""
   db_connector.db_connector.manage_dir()
   regfile = open("input_reg.csv", "a")
   for item in array:
      regfile.write(item)
   regfile.close()

print("Bem vindo ao Cashd, seus dados serão salvos em:", db_connector.WORK_DIR)
print('{:<10} {:<60}'.format('Atalho', 'Desc.'))
for c, s in mh.SHORTCUTS.items():
  print('{:<10} {:<60}'.format(c, s))

mh.prompter()
