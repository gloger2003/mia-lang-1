from enum import Enum
import enum
from pprint import pformat, pprint
from typing import Dict, List
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import mia
import utils


class MiaCommand(ABC):
    def __init__(self, mia: 'mia.Mia', t_cmd: TokenInfo, t_arg1: TokenInfo, t_arg2: TokenInfo, cmd_index: int):
        self._t_cmd = t_cmd
        self._t_arg1 = t_arg1
        self._t_arg2 = t_arg2
        self._mia = mia
        self._cmd_index = cmd_index
    
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
    
    def parse_ref(self, t: TokenInfo):
        return utils.to_ref(t)
    
    def factory(mia, t_cmd: TokenInfo, arg1: TokenInfo, arg2: TokenInfo, cmd_index: int) -> 'MiaCommand':
        key = MiaCommandsEnum[t_cmd.string]
        com: MiaCommand = CMD_MAPPING.get(key)
        return com(mia, t_cmd, arg1, arg2, cmd_index)
    
    

class AllocMiaCommand(MiaCommand):
    """
    `alloc <ref> <value>`
    -
    >>> alloc 0x1 5
    """
    
    def parse_value(self, t: TokenInfo):
        return utils.to_number_value(t)
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self.parse_value(self._t_arg2)
        self._mia.set_to_buffer(ref, val)
    

class OutMiaCommand(MiaCommand):
    """
    out <ref>
    >>> out 0x1
    """
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        self._mia.print_val(val)
        

class OutFMiaCommand(MiaCommand):
    """
    outf <ref>
    >>> outf 0x1
    """
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        self._mia.print_ref_val(ref, val)
        
        
class RegAxMiaCommand(MiaCommand):
    """
    ax <ref>
    >>> ax 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        
        self._mia.reg_ax(val)
        

class RegBxMiaCommand(MiaCommand):
    """
    bx <ref>
    >>> bx 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        val = self._mia.get_from_buffer(ref)
        
        self._mia.reg_bx(val)
        
        
class SumMiaCommand(MiaCommand):
    """
    sum -> <ref>
    >>> sum 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.sum_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        

class SubMiaCommand(MiaCommand):
    """
    sub -> <ref>
    >>> sub 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.sub_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        
        
class MulMiaCommand(MiaCommand):
    """
    mul -> <ref>
    >>> mul 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.mul_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        
        
class DivMiaCommand(MiaCommand):
    """
    div -> <ref>
    >>> div 0x1
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        self._mia.div_registers()
        
        val = self._mia.get_rx()
        self._mia.set_to_buffer(ref, val)
        

class DefNameMiaCommand(MiaCommand):
    """
    defn <str>
    >>> defn foo
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        name = self._t_arg1.string
        self._mia.add_new_def_name(name, self._cmd_index)
        
        
class CallDefNameMiaCommand(MiaCommand):
    """
    call <str>
    >>> call foo
    """
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        name = self._t_arg1.string
        self._mia.call_if_rx(name)


class MiaCommandsEnum(enum.Enum):
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
    MiaCommandsEnum.alloc: AllocMiaCommand,
    MiaCommandsEnum.out: OutMiaCommand,
    MiaCommandsEnum.ax: RegAxMiaCommand,
    MiaCommandsEnum.bx: RegBxMiaCommand,
    MiaCommandsEnum.sum: SumMiaCommand,
    MiaCommandsEnum.sub: SubMiaCommand,
    MiaCommandsEnum.div: DivMiaCommand,
    MiaCommandsEnum.mul: MulMiaCommand,
    MiaCommandsEnum.outf: OutFMiaCommand,
    MiaCommandsEnum.defn: DefNameMiaCommand,
    MiaCommandsEnum.call: CallDefNameMiaCommand,
} 