from pprint import pformat, pprint
from token import DEDENT, INDENT, NL
from typing import Dict, List, Union
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import commands as cmd
import mem
import errors


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
        

class ErrorsMixin:
    ARGS_ERROR = '================= ARGS_ERROR ================='
    KEYWORD_ERROR = '================= KEYWORD_ERROR ================='
    ASSOC_ADDRESS_ERROR = '================= ASSOC_ADDRESS_ERROR ================='
    
    def print_code_before_error(self, index_line_with_error: int):
        cur_line = 0
        for tok in self._tokens:
            if tok.start[0] < index_line_with_error:
                if cur_line != tok.start[0]:
                    print(f'{tok.start[0]}: {tok.line}', end='')
                    cur_line = tok.start[0]
        print()
            
    def print_code_after_error(self, index_line_with_error: int):
        cur_line = 0
        for tok in self._tokens:
            if tok.start[0] >= index_line_with_error + 1:
                if tok.type == ENDMARKER:
                    break
                if cur_line != tok.start[0]:
                    print(f'{tok.start[0]}: {tok.line}', end='')
                    cur_line = tok.start[0]
            
    def print_body_error(self, err_const: str, t: TokenInfo, docs: str):
        line = t.line.replace("\n", '')
        i_line = t.start[0]
        a = len(line)
        
        
        docs = '\n    | '.join([k.lstrip() for k in docs.split('\n')])
        border = "    |"
        docs = f'{border} {docs}'
        
        print(f'{err_const} on Line {i_line}\n')
        print(line)
        print('^' * a)
        print(docs)
        print()
        print(f'{err_const} on Line {i_line}\n')
        
    def _print_error(self, err_const: str, t: TokenInfo, docs: str):
        index_line_with_error = t.start[0]
        print()
        self.print_code_before_error(index_line_with_error)
        self.print_body_error(err_const, t, docs)
        self.print_code_after_error(index_line_with_error)
        print('')
    
    def print_args_error(self, t: TokenInfo, docs: str):
        self._print_error(self.ARGS_ERROR, t, docs)
        quit()
        
    def print_keyword_error(self, t: TokenInfo):
        def gen_doc(x):
            return x + ('_' * 50)
        
        docs = '\n'.join(
            [
                gen_doc(k.repr_doc())
                for k in cmd.CMD_MAPPING.values()
            ]
        )
        docs = ('_' * 50) + '\n' + docs
        self._print_error(self.KEYWORD_ERROR, t, docs)
        quit()

    def print_assoc_address_error(self, t: TokenInfo, ref: str):
        docs = '\nВы не можете напрямую записывать в эту область памяти,\n' \
            'т.к. она ассоциирована с переменной.\n\n'
        docs += repr(self._memory.get_value(ref))
        docs += '\n'
        self._print_error(self.ASSOC_ADDRESS_ERROR, t, docs)
        quit()


class IOMixin:
    def print_val(self, val):
        print(f'>>> {val}')
        
    def print_ref_val(self, ref, val):
        print(f'>>> [{ref}] = {val}')
        
    def print_welcome(self):
        print('==================|MiaLang|==================')
        print(f'= VERSION: {self.V} ')
        print('=============================================')
        print('\n')
        print(':OUT:\n')
        
    def print_buf(self):
        pprint(self._memory.get_buf_copy(), width=40)
        
    def print_assoc_buf(self):
        pprint(self._memory.get_assoc_buf_copy(), width=40)
        
        
class FlowMixin:
    def cmp_register(self):
        self._rx = self._ax == self._bx
        
    def set_cmd_index_from_def_name(self, def_name: str):
        self._cmd_index = self._def_names[def_name]
        logger.warning(f'MIA::SET_CMD_INDEX | index={self._cmd_index}')
    
    def call_if_val(self, def_name, val):
        if val > 0:
            logger.warning('MIA::CALL_IF_VAL | TRUE')
            return self.set_cmd_index_from_def_name(def_name)
        logger.warning('MIA::CALL_IF_VAL | FALSE')
    
    def call_if_rx(self, def_name):
        if self._rx > 0:
            logger.warning('MIA::CALL_IF_RX | TRUE')
            return self.set_cmd_index_from_def_name(def_name)
        logger.warning('MIA::CALL_IF_RX | FALSE')

    
class RegistersMixin:
    def reg_ax(self, val):
        self._ax = val
        logger.warning(f'MIA_CORE::REG_AX | ax={self._ax}')
        
    def reg_bx(self, val):
        self._bx = val
        logger.warning(f'MIA_CORE::REG_BX | bx={self._bx}')
        
    def reg_arxn(self, val):
        assert isinstance(val, str)
        self._arxn = val
        logger.warning(f'MIA_CORE::REG_ARXN | arxn={self._arxn}')
        
    def reg_arxi(self, val):
        assert isinstance(val, int)
        self._arxi = val
        logger.warning(f'MIA_CORE::REG_ARXI | arxi={self._arxi}')
        
    def push_value_to_array_item(self, val):
        ref = self._arxn
        array_ref = self._memory.get_value(ref)
        array_ref.set_value(val, self._arxi)
        self._arxv = val
        logger.warning(f'MIA_CORE::PUSH | arr={ref} index={self._arxi} val={val}')
        
    def get_rx(self) -> Union[int, float]:
        return self._rx
    

class Mia(OperationMixin, IOMixin, RegistersMixin, FlowMixin, ErrorsMixin):
    V = '0.0.15'

    def __init__(self, filename: str, memory_size: int):
        self._filename = filename
        self._reader = open(filename, 'rb')
        self._memory = mem.Memory(memory_size)
        
        self._cmd_index = 0
        self._def_names: Dict[str, int] = {}
        self._cmd_list: List[cmd.MiaCommand] = []
        self._tokens: List[TokenInfo] = []
        
        self._ax = 0  # var A register
        self._bx = 0  # var B register
        self._rx = 0  # Result register
        self._arxn = ''  # array_ref name register
        self._arxi = 0  # array_item[_arxi] register
        self._arxv = 0  # RES: array_item_val[_arxi]
        
    def _is_register_name(self, name: str):
        mapping = {
            '_ax': 1,
            '_bx': 2,
            '_rx': 3,
            '_arxn': 4,
            '_arxi': 5,
            '_arxv': 6
        }
        return bool(mapping.get(name))
        
    def try_get_register_value(self, reg_name: str):
        if not self._is_register_name(reg_name):
            return None
        try:
            return getattr(self, reg_name)
        except AttributeError:
            return None
    
    def define_name(self, def_name: str, cmd_index: int):
        self._def_names[def_name] = cmd_index
        
    def set_to_buffer(self, ref: str, val: Union[int, float]):
        self._memory.set_value(ref, val)
        
    def create_assoc(self, ref: str, name: str):
        self._memory.create_assoc(ref, name)
        
    def create_array(self, ref: str, name: str, length: int):
        self._memory.create_array(ref, name, length)
        
    def get_from_buffer(self, ref: str) -> Union[int, float]:
        val = self.try_get_register_value(ref)
        if val is not None:
            return val
        return self._memory.get_value(ref)
        
    def _get_clear_lines(self, tokens: List[TokenInfo]):
        # TODO: refact
        nl_indexes = []
        i = 0
        for t in tokens:
            if t.type in (NEWLINE, NL, INDENT, DEDENT):
                nl_indexes.append(i)
            i += 1
            
        lines: List[List[tokenize.TokenInfo]] = []

        start = 0
        for i in nl_indexes:
            lines.append(tokens[start:i])
            start = i + 1
        
        lines = [k for k in lines if k and k[0].string != '//']
            
        return lines
    
    def _parse_line_args(self, line: List[TokenInfo]):
        arg1 = None
        arg2 = None
        arg3 = None
        
        # TODO: refact
        try:
            arg1 = line[1]
        except IndexError:
            pass
        
        try:
            arg2 = line[2]
        except IndexError:
            pass
        
        try:
            arg3 = line[3]
        except IndexError:
            pass
        
        return arg1, arg2, arg3
        
    def _create_cmd_list(self, lines: List[List[TokenInfo]]):
        coms: List[cmd.MiaCommand] = []
        
        for line in lines:
            try:
                arg1, arg2, arg3 = self._parse_line_args(line)
                coms.append(cmd.MiaCommand.factory(self, line[0], arg1, arg2, arg3, len(coms)))
            except KeyError:
                self.print_keyword_error(line[0])
        return coms
        
    def main(self):
        self.print_welcome()
        
        tokens = tokenize.tokenize(self._reader.__next__)
        tokens = [k for k in tokens][1:]
        self._tokens = tokens
        
        lines = self._get_clear_lines(tokens)
        # pprint(lines, width=40)
        commands = self._create_cmd_list(lines)
        
        self._cmd_list = commands
        
        # pprint(commands, width=40)
        
        while self._cmd_index < len(lines):
            logger.debug(commands[self._cmd_index].__class__)
            commands[self._cmd_index].do()
            self._cmd_index += 1
                