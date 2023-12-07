import commands as cmd
from mia import Mia


kwlist = [
    cmd.MiaCommandsEnum.alloc.name
]


iskeyword = frozenset(kwlist).__contains__


mia = Mia('test.mialang', 10)

    
    