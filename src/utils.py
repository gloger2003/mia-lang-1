from pprint import pformat, pprint
from typing import Dict, List, Union
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import re


def to_number_value(t: TokenInfo) -> Union[int, float]:
    if re.match(r'^-?\d+(?:\.\d+)$', t.string) is not None:
        return float(t.string)
    if t.string.isdecimal:
        return int(t.string)
    raise TypeError('NOT NUMBER')


def to_ref(t: TokenInfo) -> str:
    return hex(int(t.string, 16))

def is_hex_ref(t: TokenInfo) -> bool:
    return t.string.startswith('0x')