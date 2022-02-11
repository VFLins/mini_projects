import db_manager as dm
import handler as hdl

def prompt_entry():
    print("\nMODO INSERÇÃO:")
    inp_date = hdl.inp_date_handle(message = "Insira a data [ddmmaaaa]: ")
    inp_time = hdl.inp_time_handle()
    inp_value = hdl.inp_float_handle()
    try:
        entry = dm.tb_entry(Data = inp_date, Hora = inp_time, Valor = inp_value)
        dm.DB_MSESSION.add(entry)
        dm.DB_MSESSION.commit()
        print("Dados armazenados!\n")
    except Exception as entry_prompter_error:
        print("Erro ao inserir dados:\n", entry_prompter_error)
    finally:
        prompt_entry()

def prompt_consult():
    print("\nMODO CONSULTA:")

    try:
        sel_mode = input("Ver tudo/Selecionar por data/Cancelar [t/d/c]: ")

        if sel_mode.upper() == "T":
            dm.querry_all_entry()
         
        elif sel_mode.upper() == "D":
            init_date = hdl.inp_date_handle(message = "Informe a data inicial [ddmmaaaa]: ")
            end_date = hdl.inp_date_handle(message = "Informe a data final [ddmmaaaa]: ")

            dm.querry_range_entry(init_date, end_date)

        elif sel_mode.upper() == "C":
            return

        else:
            print("Método inválido! Selecione algum dos métodos disponíveis.")
            prompt_consult()
    except Exception as cons_prompter_error:
        print("Erro ao ler dados:\n", cons_prompter_error, sep = "")
    finally:
        prompt_entry()

def prompt_deletion():
    print("\nMODO REMOÇÃO:")

    str_inp = input("Informe o valor de Id dos registros para remover [#,#,#,...]: ")
    dm.del_by_id_entry(str_inp)
    prompt_entry()
