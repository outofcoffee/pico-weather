# Copyright 2000-2017 JetBrains s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Delete all files and directories from a MicroPython device.

Usage:
    microdelete PORT [options]

Options:
    -v --verbose            Verbose output.
"""

import time
import sys
import os
from contextlib import suppress
from typing import List, Iterable, TypeVar, Sequence, Set

from docopt import docopt
from ampy.pyboard import Pyboard
from ampy.files import Files, DirectoryExistsError


__all__ = []

verbose = False
T = TypeVar('T')


def main(args: List[str]) -> None:
    global verbose
    opts = docopt(__doc__, argv=args)
    verbose = opts['--verbose']

    port = opts['PORT']
    print('Connecting to {}'.format(port), file=sys.stderr)
    board = Pyboard(port)
    files = Files(board)

    wait_for_board()

    while True:
        remote_files = files.ls(long_format=False, recursive=True)
        if len(remote_files) == 1:
            break

        for f in remote_files:
            if f == '/':
                continue
            print(f"Deleting {f}")
            files.rm(f)

    print('Soft reboot', file=sys.stderr, flush=True)
    soft_reset(board)


def soft_reset(board: Pyboard) -> None:
    """Perform soft-reset of the ESP8266 board."""
    board.serial.write(b'\x03\x04')


def wait_for_board() -> None:
    """Wait for some ESP8266 devices to become ready for REPL commands."""
    time.sleep(0.5)


if __name__ == '__main__':
    main(sys.argv[1:])
