# import PySimpleGUI as sgui
import msg_handler as mh
import db_connector  as dc

print("Bem vindo ao Cashd, seus dados serão salvos em:", dc.WORK_DIR)
print("Atalhos disponíveis:")
for a, b in zip(*mh.SHORTCUTS):
   print(a.ljust(10), b)

mh.prompter()
