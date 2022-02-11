import prompter as ppt
import handler as hdl
import db_manager as dm

print("Bem vindo ao Cashd, seus dados serão salvos em:", dm.WORK_DIR)
print("\nAtalhos disponíveis:")
for a, b in zip(*hdl.SHORTCUTS):
    print(a.ljust(6), b)

ppt.prompt_entry()
