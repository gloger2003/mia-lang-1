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
import errors
import utils


class MiaCommand(ABC):
    ARG1_REQUERED = False
    ARG2_REQUERED = False
    ARG3_REQUERED = False
    
    DOCS = 'CMD'
    
    def __init__(self, 
                 mia: 'mia.Mia', 
                 t_cmd: TokenInfo, 
                 t_arg1: Optional[TokenInfo], 
                 t_arg2: Optional[TokenInfo], 
                 t_arg3: Optional[TokenInfo], 
                 cmd_index: int):
        self._t_cmd: TokenInfo = t_cmd
        self._t_arg1: Optional[TokenInfo] = t_arg1
        self._t_arg2: Optional[TokenInfo] = t_arg2
        self._t_arg3: Optional[TokenInfo] = t_arg3
        self._mia = mia
        self._cmd_index = cmd_index
        
        if self.ARG1_REQUERED and self._t_arg1 is None:
            self._mia.print_args_error(self._t_cmd, self.repr_doc())
        if self.ARG2_REQUERED and self._t_arg2 is None:
            self._mia.print_args_error(self._t_cmd, self.repr_doc())
        if self.ARG3_REQUERED and self._t_arg3 is None:
            self._mia.print_args_error(self._t_cmd, self.repr_doc())
    
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
        if utils.is_hex_ref(t):
            return utils.to_ref(t)
        return t.string
    
    def factory(mia, 
                t_cmd: TokenInfo, 
                arg1: Optional[TokenInfo], 
                arg2: Optional[TokenInfo], 
                arg3: Optional[TokenInfo], 
                cmd_index: int) -> 'MiaCommand':
        key = CmdEnum[t_cmd.string]
        com: MiaCommand = CMD_MAPPING.get(key)
        return com(mia, t_cmd, arg1, arg2, arg3, cmd_index)
    

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
        try:
            self._mia.set_to_buffer(ref, val)
        except errors.AssociatedAddressError:
            self._mia.print_assoc_address_error(self._t_cmd, ref)
    

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
        self._mia.define_name(name, self._cmd_index)
        
        
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
             

class AssocCmd(MiaCommand):
    """
    `assoc <ref> <name>`
    -
    >>> assoc 0x1 a
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = True
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        name = self._t_arg2.string
        self._mia.create_assoc(ref, name)
        

class VarCmd(MiaCommand):
    """
    `var <ref> <name> <value>`
    -
    >>> var 0x1 a 10
    """
    
    def parse_value(self, t: TokenInfo):
        return utils.to_number_value(t)
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        name = self._t_arg2.string
        value = self.parse_value(self._t_arg3)
        
        self._mia.create_assoc(ref, name)
        self._mia.set_to_buffer(name, value)
        

class ArrayCmd(MiaCommand):
    """
    `array <ref> <name> <length>`
    -
    >>> array 0x1 arr 2
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = True
    ARG3_REQUERED = True
    
    def parse_value(self, t):
        return utils.to_number_value(t)

    def do(self):
        ref = self.parse_ref(self._t_arg1)
        name = self._t_arg2.string
        length = self.parse_value(self._t_arg3)

        self._mia.create_array(ref, name, length)
        
        
class RegArxnCmd(MiaCommand):
    """
    Задать значение для регистра BX по адресу из памяти
    
    `arxn <array_name>`
    -
    >>> arxn arr
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        name = self.parse_ref(self._t_arg1)
        self._mia.reg_arxn(name)
        
        
class RegArxiCmd(MiaCommand):
    """
    Задать значение для регистра BX по адресу из памяти
    
    `arxi <index>`
    -
    >>> arxi 10
    """
    
    ARG1_REQUERED = True
    ARG2_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        ref = self.parse_ref(self._t_arg1)
        try:
            val = self._mia.get_from_buffer(ref)
        except KeyError:
            if ref.isdecimal():
                val = int(ref)
        
        self._mia.reg_arxi(val)
        
        
class PushToArrayItemCmd(MiaCommand):
    """
    Задаёт значение в элемент массива: _arxn[_arxi] 
    
    `push <value>`
    -
    >>> push 10 
    """
    
    def parse_value(self, t):
        return utils.to_number_value(t)
    
    def do(self):
        try:
            val = self.parse_value(self._t_arg1)
        except ValueError:
            val = self._mia.get_from_buffer(self._t_arg1.string)
        self._mia.push_value_to_array_item(val)
       
        
class DEV_OutBufCmd(MiaCommand):
    """
    DEV_out_buf
    """
    
    ARG1_REQUERED = False
    ARG2_REQUERED = False
    ARG3_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        self._mia.print_buf()
        
        
class DEV_OutAssocBufCmd(MiaCommand):
    """
    DEV_out_assoc_buf
    """
    
    ARG1_REQUERED = False
    ARG2_REQUERED = False
    ARG3_REQUERED = False
    
    def parse_value(self):
        return super().parse_value()
    
    def do(self):
        self._mia.print_assoc_buf()
        

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
    assoc = enum.auto()
    var = enum.auto()
    array = enum.auto()
    arxn = enum.auto()
    arxi = enum.auto()
    push = enum.auto()
    
    DEV_out_buf = enum.auto()
    DEV_out_assoc_buf = enum.auto()

    
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
    CmdEnum.assoc: AssocCmd,
    CmdEnum.var: VarCmd,
    CmdEnum.array: ArrayCmd,
    CmdEnum.arxn: RegArxnCmd,
    CmdEnum.arxi: RegArxiCmd,
    CmdEnum.push: PushToArrayItemCmd,
    
    CmdEnum.DEV_out_buf: DEV_OutBufCmd,
    CmdEnum.DEV_out_assoc_buf: DEV_OutAssocBufCmd,
} 