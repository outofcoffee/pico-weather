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


"""Upload files and directories onto a MicroPython device.

Usage:
    microupload PORT PATH... [options]

Options:
    -C --chdir=PATH         Change current directory to path.
    -v --verbose            Verbose output.
"""

import time
import sys
import os
import hashlib
from contextlib import suppress
from typing import List, Iterable, TypeVar, Sequence, Set

from docopt import docopt
from ampy.pyboard import Pyboard
from ampy.files import Files, DirectoryExistsError

__all__ = []

verbose = False
T = TypeVar('T')
CACHE_DIR = '.cache'


def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_cache_path(file_path: str) -> str:
    """Get the cache file path for a given file."""
    return os.path.join(CACHE_DIR, file_path.replace(os.path.sep, '_') + '.md5')


def read_cached_hash(cache_path: str) -> str:
    """Read hash from cache file, return empty string if not found."""
    try:
        with open(cache_path, 'r') as f:
            return f.read().strip()
    except (FileNotFoundError, IOError):
        return ''


def write_cached_hash(cache_path: str, file_hash: str) -> None:
    """Write hash to cache file."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'w') as f:
        f.write(file_hash)


def should_upload_file(local_path: str) -> bool:
    """Check if file should be uploaded based on hash comparison."""
    current_hash = calculate_file_hash(local_path)
    cache_path = get_cache_path(local_path)
    cached_hash = read_cached_hash(cache_path)

    if cached_hash == current_hash:
        if verbose:
            print('  [cached, skipping]', file=sys.stderr, flush=True)
        return False
    return True


def main(args: List[str]) -> None:
    global verbose
    opts = docopt(__doc__, argv=args)
    verbose = opts['--verbose']
    paths: List[str] = opts['PATH']

    chdir = opts['--chdir']
    if chdir:
        os.chdir(chdir)

    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    port = opts['PORT']
    print('Connecting to {}'.format(port), file=sys.stderr)
    board = Pyboard(port)
    files = Files(board)

    created_cache = set()
    to_upload: List[str] = []

    for root in paths:
        rel_root = os.path.relpath(root, os.getcwd())

        wait_for_board()

        if os.path.isdir(root):
            to_upload += [os.path.join(rel_root, x)
                          for x in list_files(root)]
        else:
            to_upload += [rel_root]

    for path in progress('Uploading files', to_upload):
        local_path = os.path.abspath(path)
        remote_path = os.path.normpath(path).replace(os.path.sep, '/')

        if verbose:
            print('\n{} -> {}'.format(local_path, remote_path),
                  file=sys.stderr, end=' ', flush=True)

        if not should_upload_file(local_path):
            continue

        remote_dir = os.path.dirname(path)
        if remote_dir:
            make_dirs(files, remote_dir, created_cache)

        with open(local_path, 'rb') as fd:
            files.put(remote_path, fd.read())

        # Update cache after successful upload
        current_hash = calculate_file_hash(local_path)
        cache_path = get_cache_path(local_path)
        write_cached_hash(cache_path, current_hash)

        if verbose:
            print('[uploaded]', file=sys.stderr, flush=True)

    print('Soft reboot', file=sys.stderr, flush=True)
    soft_reset(board)


def make_dirs(files: Files, path: str,
              created_cache: Set[str] = None) -> None:
    """Make all the directories the specified relative path consists of."""
    if path == '.':
        return
    if created_cache is None:
        created_cache = set()
    parent = os.path.dirname(path)
    if parent and parent not in created_cache:
        make_dirs(files, parent, created_cache)
    with suppress(DirectoryExistsError):
        posix_path = path.replace(os.path.sep, '/')
        files.mkdir(posix_path)
        created_cache.add(path)


def soft_reset(board: Pyboard) -> None:
    """Perform soft-reset of the ESP8266 board."""
    board.serial.write(b'\x03\x04')


def list_files(path: str) -> Iterable[str]:
    """List relative file paths inside the given path."""
    for root, dirs, files in os.walk(path):
        for d in list(dirs):
            if d.startswith('.'):
                dirs.remove(d)
        for f in files:
            if not f.startswith('.'):
                yield os.path.relpath(os.path.join(root, f), path)


def wait_for_board() -> None:
    """Wait for some ESP8266 devices to become ready for REPL commands."""
    time.sleep(0.5)


def progress(msg: str, xs: Sequence[T]) -> Iterable[T]:
    """Show progress while iterating over a sequence."""
    size = len(xs)
    sys.stderr.write('\r{}: 0% (0/{})'.format(msg, size))
    sys.stderr.flush()
    for i, x in enumerate(xs, 1):
        yield x
        s = '{0}: {1}% ({2}/{3})'.format(msg, int(i * 100 / size), i, size)
        sys.stderr.write('\r' + s)
        sys.stderr.flush()
    sys.stderr.write('\n')
    sys.stderr.flush()


if __name__ == '__main__':
    main(sys.argv[1:])
