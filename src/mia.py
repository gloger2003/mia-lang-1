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


class OperationMixin:
    def sum_registers(self):
        self._rx = self._ax + self._bx
        logger.warning(f'MIA::_RX={self._rx}')
        
    def sub_registers(self):
        self._rx = self._ax - self._bx
        logger.warning(f'MIA::_RX={self._rx}')
        
    def dev_registers(self):
        self._rx = self._ax / self._bx
        logger.warning(f'MIA::_RX={self._rx}')
        
    def mul_registers(self):
        self._rx = self._ax * self._bx
        logger.warning(f'MIA::_RX={self._rx}')
    

class Mia(OperationMixin):
    def __init__(self, filename: str, memory_size: int):
        self.__filename = filename
        self.__reader = open(filename, 'rb')
        self.__memory = mem.Memory(memory_size)
        
        self._ax = None  # var A register
        self._bx = None  # var B register
        self._rx = None  # Result register
        
        self.main()
        
    def set_to_buffer(self, ref: str, val: Union[int, float]):
        self.__memory.set_val(ref, val)
        
    def get_from_buffer(self, ref: str) -> Union[int, float]:
        return self.__memory.get_val(ref)
    
    def print_val(self, val):
        print(f'>>> {val}')
        
    def reg_ax(self, val):
        self._ax = val
        logger.debug(f'MIA_CORE::REG_AX | ax={self._ax}')
        
    def reg_bx(self, val):
        self._bx = val
        logger.debug(f'MIA_CORE::REG_BX | bx={self._bx}')
        
    def get_rx(self) -> Union[int, float]:
        return self._rx
        
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
            arg1 = None
            arg2 = None
            
            # TODO: refact
            try:
                arg1 = line[1]
            except IndexError:
                pass
            
            try:
                arg2 = line[2]
            except IndexError:
                pass
            
            coms.append(cmd.MiaCommand.factory(self, line[0], arg1, arg2))
            
        pprint(coms, width=40)
        pprint(self.__memory.get_buffer_copy())
        
        print('\n\n[::OUT::]\n')
        for com in coms:
            com.do()
                