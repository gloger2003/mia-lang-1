from pprint import pformat, pprint
from typing import Dict, List
import numpy as np
from queue import LifoQueue
import tokenize
from tokenize import NEWLINE, ENDMARKER, TokenInfo

from abc import ABC, abstractmethod 
  
from loguru import logger

import commands as cmd
from mia import Mia


kwlist = [
    cmd.MiaCommandsEnum.alloc.name
]


iskeyword = frozenset(kwlist).__contains__



    
    
    

            
        
        # logger.debug(pformat(lines))


mia = Mia('test.mialang', 10)


# tokens = tokenize.tokenize(open('test.mialang', 'rb').__next__)

# pprint([k.string for k in tokens])
# print(iskeyword('alloc'))
    
    