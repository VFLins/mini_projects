import xmltodict
from datetime import datetime
import os
import db


SCRIPT_PATH = os.path.realpath(__file__)
BINDIR = os.path.join(os.path.split(SCRIPT_PATH)[0], "bin")


# VALIDATORS
###############

def valid_int(val: any):
    """
    Return `True` if `val` is of type `int` or coercible, `False` otherwise.
    """
    try:
        _ = int(val)
        return True
    except ValueError:
        return False


def valid_float(val: any):
    """
    Return `True` if `val` is of type `float` or coercible, `False` otherwise.
    """
    try:
        _ = float(val)
        return True
    except ValueError:
        return False


# PARSER
###############

class DictParser:
    """
    Classe de objeto que contém os dados de uma nota fiscal .xml em formato
    de dicionário.
    """
    def __init__(self, path: str):
        with open(path) as doc:
            self.xml = xmltodict.parse(doc.read())
        self.path = path
        self.key = self.get_key()

        self.erroed: bool = False
        self.err: Exception | None = None

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, err_type, err_val, traceback):
        pass

    def get_pay(self):
        """return the payment section of the `.xml` in ``"""
        try:
            pay = self.xml["NFe"]["infNFe"]["total"]["ICMSTot"]["pag"]["detPag"]
        except KeyError:
            try:
                pay = self.xml["nfeProc"]["NFe"]["infNFe"]["pag"]["detPag"]
            except KeyError:
                pay = self.xml["NFe"]["infNFe"]["pag"]
        if type(pay["detPag"]) is list:
            return {
                "type": ";".join([x["tPag"] if valid_int(x) else "NaN" for x in pay]),
                "amount": ";".join(
                    [x["vPag"] if valid_float(x) else "NaN" for x in pay]
                ),
            }
        else:
            return {"type": pay["detPag"]["tPag"], "amount": pay["detPag"]["vPag"]}

    def get_key(self):
        try:
            return self.xml["nfeProc"]["NFe"]["infNFe"]["@Id"][3:]
        except KeyError:
            return self.xml["NFe"]["infNFe"]["@Id"][3:]

    def get_dt(self):
        try:
            dt = self.xml["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"]
        except KeyError:
            dt = self.xml["NFe"]["infNFe"]["ide"]["dhEmi"]
        return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")

    def get_total(self):
        try:
            total = self.xml["nfeProc"]["NFe"]["infNFe"]["total"]["ICMSTot"]
        except KeyError:
            total = self.xml["NFe"]["infNFe"]["total"]["ICMSTot"]

        if valid_float(total["vNF"]):
            products = total["vNF"]

        if valid_float(total["vTotTrib"]):
            taxes = total["vTotTrib"]

        # expected to not appear sometimes, will not raise
        discount = "0"
        if "vDesc" in total.keys():
            if valid_float(total["vDesc"]):
                discount = total["vDesc"]

        return {"products": products, "discount": discount, "taxes": taxes}

    def parse(self):
        try:
            key = self.get_key()
            dt = self.get_dt()
            pay = self.get_pay()
            total = self.get_total()
        except Exception as err:
            self.erroed = True
            self.err = err
            return

        self.data = {
            "ChaveNFe": key,
            "DataHoraEmi": dt,
            "PagamentoTipo": pay["type"],
            "PagamentoValor": pay["amount"],
            "TotalProdutos": total["products"],
            "TotalDesconto": total["discount"],
            "TotalTributos": total["taxes"],
        }

        try:
            self.rowdata = db.RowElemSales(**self.data)
        except Exception as err:
            self.erroed = True
            self.err = err
            return
