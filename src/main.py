import sys

from loguru import logger
from mia import Mia


if len(sys.argv) > 2:
    if sys.argv[2] == 'clear':
        logger.remove()


mia = Mia(sys.argv[1], 100)
mia.main()
