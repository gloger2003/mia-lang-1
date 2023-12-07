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
        return f'{self.__class__}<ref={self._ref} name={self._name} value={self._value}>'
        
    def set_value(self, val):
        self._value = val
        
    def get_value(self):
        return self._value
    
    
class ArrayItem:
    def __init__(self, array_ref: 'ArrayRef', ref: str, index: int):
        self._array_ref = array_ref
        self._ref = ref
        self._index = index
        self._value = None
        
    def __repr__(self) -> str:
        return f'{self.__class__}<ref={self._ref} index={self._index} value={self._value} array_ref={self._array_ref._name}>'
        
    def set_value(self, value):
        self._value = value
        
    def get_value(self):
        return self._value
    
    def reg_me(self):
        self._array_ref.reg_array_item(self)
        
    def get_ref(self) -> str:
        return self._ref


class ArrayRef(AssocRef):
    def __init__(self, ref: str, name: str, length: int):
        super().__init__(ref, name)
        self._length = length
        
        self._array_values: List[ArrayItem] = []
        
    def reg_array_item(self, item: ArrayItem):
        self._array_values.append(item)

    def get_item_generator(self):
        start = int(self._ref, 16)
        for i, k in enumerate(range(start, start + self._length + 1, 1)):
            yield ArrayItem(self, hex(k), i)
        
    def set_value(self, index, value):
        pass
    
    def get_value(self, index=None):
        if index is None:
            return [k.get_value() for k in self._array_values] 


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
            array_ref = self.__buffer.get(assoc_ref)
            if isinstance(array_ref, ArrayRef):
                logger.success(f'MEMORY::GET_VAL | array_ref={ref} | val={assoc_ref}')
                return array_ref
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

    def get_buf_copy(self) -> Dict:
        return self.__buffer.copy()
    
    def get_assoc_buf_copy(self) -> Dict:
        return self.__assoc_buffer.copy()

    def create_array(self, ref: str, name: str, length: int):
        array = ArrayRef(ref, name, length)
        
        for item in array.get_item_generator():
            item_ref = item.get_ref()
            # TODO: check buffer
            self.__buffer[item_ref] = item
            item.reg_me()

        self.__assoc_buffer[name] = ref
        self.__buffer[ref] = array
            
            