import prompter as ppt
import msg_handler as mh
import db_manager as dm

print("Bem vindo ao Cashd, seus dados serão salvos em:", dm.WORK_DIR)
print("\nAtalhos disponíveis:")
for a, b in zip(*mh.SHORTCUTS):
   print(a.ljust(10), b)
print("")

ppt.prompter()
