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
    def __init__(self, mia: 'mia.Mia', t_cmd: TokenInfo, t_arg1: TokenInfo, t_arg2: TokenInfo):
        self._t_cmd = t_cmd
        self._t_arg1 = t_arg1
        self._t_arg2 = t_arg2
        self._mia = mia
    
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
    
    def factory(mia, t_cmd: TokenInfo, arg1: TokenInfo, arg2: TokenInfo) -> 'MiaCommand':
        key = MiaCommandsEnum[t_cmd.string]
        com: MiaCommand = CMD_MAPPING.get(key)
        return com(mia, t_cmd, arg1, arg2)
    
    

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
        print(val)


class MiaCommandsEnum(enum.Enum):
    alloc = 0
    out = 1

    
CMD_MAPPING = {
    MiaCommandsEnum.alloc: AllocMiaCommand,
    MiaCommandsEnum.out: OutMiaCommand
} 