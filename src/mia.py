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
        

class IOMixin:
    def print_val(self, val):
        print(f'>>> {val}')
        
    def print_ref_val(self, ref, val):
        print(f'>>> [{ref}] = {val}')
        
        
class FlowMixin:
    def cmp_register(self):
        self._rx = self._ax == self._bx
        
    def set_cmd_index_from_def_name(self, def_name: str):
        self._cmd_index = self._def_names[def_name]
        logger.warning(f'MIA::SET_CMD_INDEX | index={self._cmd_index}')
    
    def call_if_val(self, def_name, val):
        pass
    
    def call_if_rx(self, def_name):
        if self._rx > 0:
            return self.set_cmd_index_from_def_name(def_name)
        logger.warning('MIA::CALL_IF_RX | FALSE')

    
class RegistersMixin:
    def reg_ax(self, val):
        self._ax = val
        logger.debug(f'MIA_CORE::REG_AX | ax={self._ax}')
        
    def reg_bx(self, val):
        self._bx = val
        logger.debug(f'MIA_CORE::REG_BX | bx={self._bx}')
        
    def get_rx(self) -> Union[int, float]:
        return self._rx
    

class Mia(OperationMixin, IOMixin, RegistersMixin, FlowMixin):
    def __init__(self, filename: str, memory_size: int):
        self.__filename = filename
        self.__reader = open(filename, 'rb')
        self.__memory = mem.Memory(memory_size)
        
        self._cmd_index = 0
        self._def_names: Dict[str, int] = {}
        
        self._ax = None  # var A register
        self._bx = None  # var B register
        self._rx = None  # Result register
    
    def add_new_def_name(self, def_name: str, cmd_index: int):
        self._def_names[def_name] = cmd_index
        
    def set_to_buffer(self, ref: str, val: Union[int, float]):
        self.__memory.set_val(ref, val)
        
    def get_from_buffer(self, ref: str) -> Union[int, float]:
        return self.__memory.get_val(ref)
        
    def get_clear_lines(self, tokens: List[TokenInfo]):
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
            
        return lines
    
    def parse_line_args(self, line: List[TokenInfo]):
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
        
        return arg1, arg2
        
    def create_cmd_list(self, lines: List[List[TokenInfo]]):
        coms: List[cmd.MiaCommand] = []
        for line in lines:
            arg1, arg2 = self.parse_line_args(line)
            coms.append(cmd.MiaCommand.factory(self, line[0], arg1, arg2, len(coms)))
        return coms
        
    def main(self):
        tokens = tokenize.tokenize(self.__reader.__next__)
        tokens = [k for k in tokens][1:]
        
        lines = self.get_clear_lines(tokens)
        commands = self.create_cmd_list(lines)
        
        # pprint(coms, width=40)
        # pprint(self.__memory.get_buffer_copy())
        
        while self._cmd_index < len(lines):
            commands[self._cmd_index].do()
            self._cmd_index += 1
                