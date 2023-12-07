import sys

from loguru import logger
import commands as cmd
from mia import Mia


kwlist = [
    cmd.MiaCommandsEnum.alloc.name
]


iskeyword = frozenset(kwlist).__contains__


if len(sys.argv) > 1:
    if sys.argv[1] == 'clear':
        logger.remove()


mia = Mia('test.mialang', 10)
mia.main()

    