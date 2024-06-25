import os
import pickle
import parse
import db


# CONSTANTS
###############

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.split(SCRIPT_PATH)[0]
CACHE_FILE = os.path.join(SCRIPT_DIR, "processed_files.cache")

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
    jobs = (parse.DictParser(f) for f in new_nfes)
    for fileparser in jobs:
        fileparser.parse()
        if not fileparser.erroed:
            try:
                row = db.RowElemSales(**fileparser.data)
            except Exception as err:
                fileparser.erroed = True
                fileparser.err = err
            db.insert_sale(row)
            success.append(fileparser.path)
        else:
            fail.append(fileparser)

if __name__ == "__main__":
    pass
