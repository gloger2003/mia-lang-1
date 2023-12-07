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


class MemoryRef:
    def __init__(self, key_ref: int):
        pass



class Mia:
    def __init__(self, filename: str, memory_size: int):
        self.__filename = filename
        self.__reader = open(filename, 'rb')
        self.__memory = Memory(memory_size)
        
        self.main()
        
    def set_to_buffer(self, ref: int, val: Union[int, float]):
        self.__memory.set_val(ref, val)
        
    def main(self):
        tokens = tokenize.tokenize(self.__reader.__next__)
        tokens = [k for k in tokens][1:]
        
        # TODO: refact
        nl_indexes = []
        i = 0
        for t in tokens:
            if t.type == NEWLINE:
                nl_indexes.append(i)
            i += 1
            
        lines: List[List[tokenize.TokenInfo]] = []

        start = 0
        for i in nl_indexes:
            lines.append(tokens[start:i])
            start = i + 1
        
        coms: List[cmd.MiaCommand] = []
        for line in lines:
            coms.append(cmd.MiaCommand.factory(self, line[0], line[1], line[2]))
            
        for com in coms:
            com.do_it()
                
        pprint(coms)