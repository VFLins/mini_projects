from datetime import datetime
from typing import List
import sqlite3
import re
import os


# CONSTANTS
###############

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.split(SCRIPT_PATH)[0]
DB_PATH = r"C:\databases\pdv.sqlite"


def create_table(table: str):
    """Create table if doesn't exist"""
    dbcon = sqlite3.connect(DB_PATH)
    dbcur = dbcon.cursor()
    dbcur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
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
    dbcon.close()


class KeyType(str):
    def __init__(self) -> None:
        super().__init__()


class DTType(str):
    def __init__(self) -> None:
        super().__init__()


class ListOfNumbers(str):
    def __init__(self) -> None:
        super().__init__()


class FloatCoercible(str):
    def __init__(self) -> None:
        super().__init__()


class RowElem:
    def __init__(
        self,
        ChaveNFe: KeyType,
        DataHoraEmi: DTType,
        PagamentoTipo: ListOfNumbers,
        PagamentoValor: ListOfNumbers,
        TotalProdutos: FloatCoercible,
        TotalDesconto: FloatCoercible,
        TotalTributos: FloatCoercible,
    ):
        
        self.ChaveNFe = ChaveNFe
        self.DataHoraEmi = DataHoraEmi
        self.PagamentoTipo = PagamentoTipo
        self.PagamentoValor = PagamentoValor
        self.TotalProdutos = TotalProdutos
        self.TotalDesconto = TotalDesconto
        self.TotalTributos = TotalTributos

        self._validate_all()

    def _valid_key(key):
        if len(key) == 44 and type(key) == str:
            return True
        return False

    def _valid_dt(dt):
        try:
            _ = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")
            return True
        except Exception:
            return False

    def _valid_list_of_numbers(string):
        pattern = r"^[0-9;.]+$"
        return bool(re.match(pattern, string))

    def _valid_float(floating_point):
        try:
            _ = float(floating_point)
            return True
        except ValueError:
            return False

    def _validate_all(self):
        types = self.__init__.__annotations__

        for var in type.keys():
            value = getattr(self, var)

            if types[var] == KeyType:
                if not self._valid_key(value):
                    raise ValueError(f"Invalid value in {var}: {value}")

            if types[var] == DTType:
                if not self._valid_dt(value):
                    raise ValueError(f"Invalid value in {var}: {value}")

            if types[var] == ListOfNumbers:
                if not self._valid_list_of_numbers(value):
                    raise ValueError(f"Invalid value in {var}: {value}")

            if types[var] == FloatCoercible:
                if not self._valid_float(value):
                    raise ValueError(f"Invalid value in {var}: {value}")


def insert_row(row: RowElem, table: str):
    """Inserts a `RowElem` as a row to `table`."""
    if not type(row) == RowElem:
        raise TypeError(f"Expected type `RowElem`, got {type(row)}")
    
    create_table(table=table)

    dbcon = sqlite3.connect(DB_PATH)
    dbcur = dbcon.cursor()
    dbcur.execute(
        f"""
        INSERT INTO {table} (
            ChaveNFe,
            DataHoraEmi,
            PagamentoTipo,
            PagamentoValor,
            TotalProdutos,
            TotalDesconto,
            TotalTributos
        ) VALUES (
            {row.ChaveNFe},
            {row.DataHoraEmi},
            {row.PagamentoTipo},
            {row.PagamentoValor},
            {row.TotalProdutos},
            {row.TotalDesconto},
            {row.TotalTributos}
        );
        """
    )
    dbcon.close()
