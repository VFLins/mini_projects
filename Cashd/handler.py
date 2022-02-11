import datetime as dt
from collections import OrderedDict
import prompter as ppt
from time import sleep

SHORTCUTS = (
    OrderedDict( {
        "HOJE" : "date", 
        "AGORA" : "time", 
        "CONS" : "call", 
        "REM" : "call"}
    ),
    ["Retorna a data atual em um campo válido",
    "Retorna o horário atual em um campo válido",
    "Cancela a entrada atual de dados e entra no modo de consluta",
    "Cancela a entrada atual de dados e entra no modo de remoção"]
)

def countdown_message(message, error, seconds = 15):
    print("\n", message, error, end = "\n", sep = "\n")
    while seconds > 0:
        PSECONDS = "{:0>2d}".format(seconds)
        print("Fechando em ...", PSECONDS, end = "\r", sep = "")
        sleep(1)
        seconds -= 1
    quit()

def inp_date_handle(message) -> dt.date:
    """
    Returns input from the user as a datetime.date object.
    Also deals with attributable shortcuts.
    """
    def str_to_date(str):
        date = dt.date(
            year = int( str[4:] ), 
            month = int( str[2:4] ), 
            day = int( str[0:2] ))
        return date

    def is_date_type(x) -> bool:
        try: return isinstance( x, type(dt.date.today()) )
        except: return False

    str_input = input(message)
    try:
        if str_input.upper() in SHORTCUTS[0].keys():
            try: tru_date = shortcut_handle(str_input, type = "date")
            except:
                print("Valor inválido para data!")
                inp_date_handle(message)
        else:
            try: tru_date = str_to_date(str_input)
            except:
                print("Valor inválido para data!")
                inp_date_handle(message)

        if is_date_type(tru_date): 
            return tru_date
        else: 
            inp_date_handle(message)
    except Exception as ERROR:
        countdown_message("ERRO IMPREVISTO AO ATRIBUIR DATA:", error = ERROR)

def inp_time_handle() -> dt.time:
    """
    Returns input from the user as datetime.time object.
    """
    def str_to_time(str):
        time = dt.time(
            second = int( str[4:] ),
            minute = int( str[2:4] ),
            hour = int( str[0:2] ))
        return time

    def is_time_type(x) -> bool:
        try: return isinstance( x, type(dt.datetime.now().time()) )
        except: return False

    str_input = input("Insira o horário [hhmmss]: ")
    try:
        if str_input.upper() in SHORTCUTS[0].keys():
            try: tru_time = shortcut_handle(str_input, type = "time")
            except:
                print("Valor inválido para horário!")
                inp_time_handle()
        else:
            try: tru_time = str_to_time(str_input)
            except:
                print("Valor inválido para horário!")
                inp_time_handle()
      
        if is_time_type(tru_time):
            return tru_time
        else:
            inp_time_handle()
    except Exception as ERROR:
        countdown_message("ERRO IMPREVISTO AO ATRIBUIR HORÁRIO:", error = ERROR)

def inp_float_handle() -> float:
    """
    Returns input from the user as float object.
    """
    def str_to_numeric(str):
        return float(str)

    def is_numeric_type(x) -> bool:
        try:
            if isinstance(x, bool): return False
            else: return isinstance(x, (int, float))
        except:
            return False

    str_input = input("Insira o valor [0000.00]: ")
    try:
        if str_input.upper() in SHORTCUTS[0].keys():
            try: tru_numeric = shortcut_handle(str_input)
            except:
                print("Verifique se está separando as casas decimais com ponto!")
                inp_float_handle()
        else:
            try: tru_numeric = str_to_numeric(str_input)
            except:
                print("Verifique se está separando as casas decimais com ponto!")
                inp_float_handle()

        if is_numeric_type(tru_numeric):
            return tru_numeric
        else:
            inp_float_handle()
    except Exception as ERROR:
        countdown_message("ERRO AO ATRIBUIR VALOR:", error = ERROR)

def shortcut_handle(shortcut, type = "call"):

    def keys_by_value(dict, value):
        KEYS_LIST = list()
        ITEMS_LIST = dict.items()
        for item  in ITEMS_LIST:
            if item[1] == value:
                KEYS_LIST.append(item[0])
        return  KEYS_LIST

    # Shortcut inserted must be of the type informed and call
    SEL_SHORTCUTS = keys_by_value(SHORTCUTS[0], "call")
    if  type != "call":
        for item in keys_by_value(SHORTCUTS[0], type):
            SEL_SHORTCUTS.append( item )

    # Raise ValueError if shortcut not allowed
    if shortcut.upper() not in SEL_SHORTCUTS:
        raise ValueError
    # Deal with shortcut if valid and allowed
    else:
        if shortcut.upper() == "HOJE":
            output = dt.date.today()
            return output
        elif shortcut.upper() == "AGORA":
            output = dt.datetime.now().time().replace(microsecond = 0)
            return output
        elif shortcut.upper() == "CONS":
            ppt.prompt_consult()
        elif shortcut.upper() == "REM":
            ppt.prompt_deletion()
