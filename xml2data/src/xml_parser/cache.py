import pickle
from os import path


SCRIPT_PATH = path.split(path.realpath(__file__))[0]
CACHE_PATH = path.join(SCRIPT_PATH, "cache")
CACHE_TYPES = ["parsed", "failed", "keys"]

def get_parsed(type_idx: int):
    """
    ### Args:
    - type_idx (`int`): index from ["parsed", "failed", "keys"]

    ### Returns:
    - `list` of `xml_parser.parse.DictParser` elements for type_idx < 2

    or
    
    - `list` of `str` for type_idx == 2
    """
    filepath = path.join(CACHE_PATH, CACHE_TYPES[type_idx]) 
    with open(filepath, "rb") as cachefile:
        pass