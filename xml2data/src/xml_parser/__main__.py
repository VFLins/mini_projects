import os
import pickle
import parse
import db


# CONSTANTS
###############

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.split(SCRIPT_PATH)[0]
CACHE_FILE = os.path.join(SCRIPT_DIR, "processed_files.cache")
DB_PATH = r"C:\databases\pdv.sqlite"


# DATABASE
###############

# create tables if doesn't exist
dbcon = sqlite3.connect(DB_PATH)
dbcur = dbcon.cursor()
dbcur.execute(
    """
    CREATE TABLE IF NOT EXISTS sales (
        Id INTEGER PRIMARY KEY,
        ChaveNFe TEXT NOT NULL UNIQUE,
        DataHoraEmi TEXT,
        PagamentoTipo TEXT,
        PagamentoValor TEXT,
        TotalProdutos REAL,
        TotalDesconto REAL,
        TotalTributos REAL
    )
    """
)


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
    def __init__(self, path: str):
        with open(path) as doc:
            self.xml = xmltodict.parse(doc.read())
        self.path = path

        self.data = None
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

    def parse(self) -> db.RowElem:
        try:
            data = {
                "key": self.get_key(),
                "dt": self.get_dt(),
                "pay": self.get_pay(),
                "total": self.get_total()
            }
        except Exception as err:
            self.erroed = True
            self.err = err
            return

        self.data = {
            "ChaveNFe": data["key"],
            "DataHoraEmi": data["dt"],
            "PagamentoTipo": data["pay"]["type"],
            "PagamentoValor": data["pay"]["amount"],
            "TotalProdutos": data["total"]["products"],
            "TotalDesconto": data["total"]["discount"],
            "TotalTributos": data["total"]["taxes"]}

    def get_rowdata(self):
        if not self.data:
            self.parse()
        try:
            self.rowdata = db.RowElem(**self.data)
            return self.rowdata
        except Exception as err:
            self.erroed = True
            self.err = err


class DictParserSales(DictParser):
    def __init__(self, path: str):
        super().__init__(path)
    
    def get_rowdata(self):
        if not self.data:
            self.parse()
        try:
            self.rowdata = db.RowElemSales(**self.data)
            return self.rowdata
        except Exception as err:
            self.erroed = True
            self.err = err

# RUN
###############

def run(retry_failed = False):
    # 1. [DONE] get list of processable files
    # 2. [DONE] get list of already processed
    # 3. [DONE] parse unprocessed
    # 4. [DONE] insert data
    # 5. save stats
    PASTA_VENDAS = r"C:\GDOOR Sistemas\GDOOR SLIM\NFCe\XML\Vendas"
    nfes = [
        os.path.join(PASTA_VENDAS, filename)
        for filename in os.listdir(PASTA_VENDAS)
        if len(filename) > 10
    ]

    with open(CACHE_FILE) as cache:
        cache: dict = pickle.load(cache)
        processed_nfes = cache["sucess"]
        if not retry_failed:
            processed_nfes = processed_nfes + cache["fail"]
        new_nfes = nfes not in processed_nfes

    fail = []
    success = []
    jobs = (DictParserSales(f) for f in new_nfes)
    for fileparser in jobs:
        row = fileparser.get_rowdata()
        if row:
            db.insert_sale(row)
            success.append(fileparser.path)
        else:
            fail.append(fileparser)

if __name__ == "__main__":
    pass
