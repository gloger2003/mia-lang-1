from pprint import pformat, pprint
from typing import Dict, List, Union
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger
import errors
import commands as cmd


class AssocRef:
    def __init__(self, ref: str, name: str):
        self._ref = ref
        self._name = name
        self._value = None
        
    def __repr__(self) -> str:
        return f'AssocRef<ref={self._ref} name={self._name} value={self._value}>'
        
    def set_value(self, val):
        self._value = val
        
    def get_value(self):
        return self._value


class Memory:
    def __init__(self, size: int = 10):
        assert size % 2 == 0
        self.__size = size
        self.__buffer: Dict[str, Union[int, float, AssocRef]] = {}
        self.__assoc_buffer: Dict[str, int] = {}

        self.fill_memory()

    def fill_memory(self):
        self.__buffer = {hex(k): None for k in range(int(self.__size / 2))}
        # self.__assoc_buffer = {None: hex(k) for k in range(int(self.__size / 2))}
        logger.debug(self.__buffer)
        logger.debug(self.__assoc_buffer)
        
    def check_ref(self, ref: str):
        pass
        
    def set_value(self, ref: str, val: Union[int, float]):
        assoc_ref = self.__assoc_buffer.get(ref)
        
        # TODO: refact
        if assoc_ref is not None:
            assoc = self.__buffer[assoc_ref]
            assoc.set_value(val)
            logger.success(f'MEMORY::SET_VAL | assoc_ref={assoc_ref} | val={val}')
        else:
            if isinstance(self.__buffer[ref], AssocRef):
                raise errors.AssociatedAddressError()
            self.__buffer[ref] = val
            logger.success(f'MEMORY::SET_VAL | ref={ref} | val={val}')
        
    def get_value(self, ref: str) -> Union[int, float]:
        assoc_ref = self.__assoc_buffer.get(ref)
        
        if assoc_ref is not None:
            val = self.__buffer[assoc_ref].get_value()
            logger.success(f'MEMORY::GET_VAL | assoc_ref={ref} | val={val}')
        else:
            val = self.__buffer[ref]
            logger.success(f'MEMORY::GET_VAL | ref={ref} | val={val}')
        return val
    
    def create_assoc(self, ref: str, name: str):
        assoc = AssocRef(ref, name)
        
        self.__assoc_buffer[name] = ref
        self.__buffer[ref] = assoc

    def get_buffer_copy(self) -> Dict:
        return self.__buffer.copy()


class MemoryRef:
    def __init__(self, key_ref: int):
        pass