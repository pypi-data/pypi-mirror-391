# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
h2 tank optimization
"""

import logging
import sys

from patme.service.logger import log

from tankoh2.__about__ import __author__, __description__, __programDir__, __title__, __version__
from tankoh2.settings import PychainWrapper

# main program information
name = __title__
programDir = __programDir__
version = __version__
description = __description__
author = __author__

# create logger
log.addFileHandlers(programDir, "run.log", "debug.log")

# make mycropychain available
pychainIsLoaded = False
pychain = PychainWrapper()
