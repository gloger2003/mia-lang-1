import sys

from loguru import logger
from mia import Mia


if len(sys.argv) > 1:
    if sys.argv[1] == 'clear':
        logger.remove()


mia = Mia('test.mialang', 20)
mia.main()
