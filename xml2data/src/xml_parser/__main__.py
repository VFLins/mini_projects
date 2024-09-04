import os
import cache
from parse import DictParser
import db


# CONSTANTS
###############

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.split(SCRIPT_PATH)[0]
CACHE_FILE = os.path.join(SCRIPT_DIR, "processed_files.cache")
DB_PATH = os.path.join(SCRIPT_DIR, "data", "main.sqlite")


# RUN
###############

def run_failed(path: str):
    pass

def run(path: str, retry_failed = False):
    # 1. [DONE] get list of processable files
    # 2. [DONE] get list of already processed (success and fail)
    # 3. [DONE] parse
    # 4. [DONE] insert data
    # 5. save list of already processed (success and fail)

    nfes = [
        os.path.join(path, filename)
        for filename in os.listdir(path)
        if (len(filename) > 10) and (".xml" in filename)
    ]

    with open(CACHE_FILE) as cache:
        cache: dict = cache.load(cache) # !!!
        processed_nfes = cache["sucess"]
        if not retry_failed:
            processed_nfes = processed_nfes + cache["fail"]
        new_nfes = nfes not in processed_nfes

    fail = []
    success = []
    jobs = (DictParser(f) for f in new_nfes)
    for fileparser in jobs:
        row = fileparser.get_rowdata()
        if row:
            db.insert_sale(row)
            success.append(fileparser.path)
        else:
            fail.append(fileparser)

if __name__ == "__main__":
    pass
