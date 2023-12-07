from enum import Enum
import enum
from pprint import pformat, pprint
from typing import Dict, List, Optional
import numpy as np
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import mia
import utils


class MiaCommand(ABC):
    ARG1_REQUERED = False
    ARG2_REQUERED = False
    DOCS = 'CMD'
    
    def __init__(self, mia: 'mia.Mia', t_cmd: TokenInfo, t_arg1: TokenInfo, t_arg2: TokenInfo, cmd_index: int):
        self._t_cmd: TokenInfo = t_cmd
        self._t_arg1: Optional[TokenInfo] = t_arg1
        self._t_arg2: Optional[TokenInfo] = t_arg2
        self._mia = mia
        self._cmd_index = cmd_index
        
        if self.ARG1_REQUERED and self._t_arg1 is None:
            self._mia.print_error_args(self._t_cmd, self.repr_doc())
        if self.ARG2_REQUERED and self._t_arg2 is None:
            self._mia.print_error_args(self._t_cmd, self.repr_doc())
    
    def __repr__(self) -> str:
        cmd = self._t_cmd.string
        arg1 = self._t_arg1.string if self._t_arg1 is not None else None
        arg2 = self._t_arg2.string if self._t_arg2 is not None else None
        return f'< {cmd.upper()} | {arg1} : {arg2} >'
        
    @abstractmethod
    def do(self):
        pass
    
    @abstractmethod
    def parse_value(self):
        pass

    @classmethod
    def repr_doc(cls):
        return cls.__doc__.replace('`', '').replace('-\n','\n')

    def parse_ref(self, t: TokenInfo):
        return utils.to_ref(t)
    
    def factory(mia, t_cmd: TokenInfo, arg1: TokenInfo, arg2: TokenInfo, cmd_index: int) -> 'MiaCommand':
        key = CmdEnum[t_cmd.string]
        com: MiaCommand = CMD_MAPPING.get(key)
        return com(mia, t_cmd, arg1, arg2, cmd_index)
    

class AllocCmd(MiaCommand):
    """
    Размещение значения в памяти по адресу
    
    `alloc <ref> <value>`
    -
    >>> alloc 0x1 5
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = True
    
    def parse_value(self, t: TokenInfo):
        return utils.to_number_value(t)
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self.parse_value(self._t_arg2)
        self._mia.set_to_buffer(ref, val)
    

class OutCmd(MiaCommand):
    """
    Вывод значения по адресу из памяти в консоль 
    
    `out <ref>`
    -
    >>> out 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        self._mia.print_val(val)
        

class OutFCmd(MiaCommand):
    """
    Вывод [адреса]=[значение] по адресу из памяти в консоль
    
    `outf <ref>`
    -
    >>> outf 0x1
    """
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        self._mia.print_ref_val(ref, val)
        
        
class RegAxCmd(MiaCommand):
    """
    Задать значение для регистра AX по адресу из памяти
    
    `ax <ref>`
    -
    >>> ax 0x1
    """
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        
        self._mia.reg_ax(val)
        

class RegBxCmd(MiaCommand):
    """
    Задать значение для регистра BX по адресу из памяти
    
    `bx <ref>`
    -
    >>> bx 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        
        self._mia.reg_bx(val)
        
        
class SumCmd(MiaCommand):
    """
    `sum -> <ref>`
    -
    >>> sum 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.sum_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        

class SubCmd(MiaCommand):
    """
    `sub -> <ref>`
    -
    >>> sub 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.sub_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        
        
class MulCmd(MiaCommand):
    """
    `mul -> <ref>`
    -
    >>> mul 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.mul_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        
        
class DivCmd(MiaCommand):
    """
    `div -> <ref>`
    -
    >>> div 0x1
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.div_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        

class DefNameCmd(MiaCommand):
    """
    `defn <str>`
    -
    >>> defn foo
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        name = self._t_arg1.string
        self._mia.add_new_def_name(name, self._cmd_index)
        
        
class CallDefNameCmd(MiaCommand):
    """
    `call <str>`
    -
    >>> call foo
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        name = self._t_arg1.string
        if self._t_arg2 is None:
            return self._mia.call_if_rx(name)
        ref = self.parse_ref(self._t_arg2)
        val = self._mia.get_from_buffer(ref)
        self._mia.call_if_val(name, val)


class CmdEnum(enum.Enum):
    alloc = 0
    out = enum.auto()
    ax = enum.auto()
    bx = enum.auto()
    sum = enum.auto()
    sub = enum.auto()
    div = enum.auto()
    mul = enum.auto()
    outf = enum.auto()
    defn = enum.auto()
    call = enum.auto()

    
CMD_MAPPING = {
    CmdEnum.alloc: AllocCmd,
    CmdEnum.out: OutCmd,
    CmdEnum.ax: RegAxCmd,
    CmdEnum.bx: RegBxCmd,
    CmdEnum.sum: SumCmd,
    CmdEnum.sub: SubCmd,
    CmdEnum.div: DivCmd,
    CmdEnum.mul: MulCmd,
    CmdEnum.outf: OutFCmd,
    CmdEnum.defn: DefNameCmd,
    CmdEnum.call: CallDefNameCmd,
} 