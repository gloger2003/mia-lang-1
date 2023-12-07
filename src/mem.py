from pprint import pformat, pprint
from typing import Dict, List, Union
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import commands as cmd


class Memory:
    def __init__(self, size: int = 10):
        self.__size = size
        self.__buffer: Dict[int, str] = {}

        self.fill_memory()

    def fill_memory(self):
        self.__buffer = {hex(k): None for k in range(self.__size)}
        logger.debug(self.__buffer)
        
    def check_ref(self, ref: str):
        pass
        
    def set_val(self, ref: str, val: Union[int, float]):
        self.__buffer[ref]
        self.__buffer[ref] = val
        logger.success(f'MEMORY::SET_VAL | ref={ref} | val={val}')
        pprint(self.__buffer)
        
    def get_val(self, ref: str) -> Union[int, float]:
        return self.__buffer[ref]


class MemoryRef:
    def __init__(self, key_ref: int):
        pass