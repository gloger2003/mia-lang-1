from pprint import pformat, pprint
from typing import Dict, List, Union
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import commands as cmd
import mem


class Mia:
    def __init__(self, filename: str, memory_size: int):
        self.__filename = filename
        self.__reader = open(filename, 'rb')
        self.__memory = mem.Memory(memory_size)
        
        self.main()
        
    def set_to_buffer(self, ref: str, val: Union[int, float]):
        self.__memory.set_val(ref, val)
        
    def get_from_buffer(self, ref: str) -> Union[int, float]:
        return self.__memory.get_val(ref)
        
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
            com.do()
                
        pprint(coms)