#!/usr/bin/env python

import argparse
import os
import os.path
import re
import subprocess
import sys
import typing

LUPDATE = 'lupdate'

LRELEASE = 'lrelease'

QT_VER = 6

TRANSLATIONS: list[str] = [
  'ja',
]

SRCS: list[str] = [
  'kb_ui',
  'app',
]

def build_lupd_flags(inputs: list[str],
                     out_path: str,
                     no_recursive: bool = True,
                     extensions: typing.Optional[list[str]] = None,
                     no_sort: bool = True) -> list[str]:
  res = []
  if no_recursive:
    res.append('-no-recursive')
  if extensions is None:
    extensions = ['py']
  if len(extensions) > 0:
    res.extend(['-extensions', ','.join(extensions)])
  if no_sort:
    res.append('-no-sort')
  res.extend(['-ts', out_path])
  res.extend(inputs)
  return res

def build_lrel_flags(inputs: list[str],
                     out_path: str,
                     no_unfinished: bool = True,
                     remove_identical: bool = True) -> list[str]:
  res = []
  if no_unfinished:
    res.append('-nounfinished')
  if remove_identical:
    res.append('-removeidentical')
  res.extend(['-qm', out_path])
  res.extend(inputs)
  return res

def build_py_filename(name: str) -> str:
  return name + '.py'

def build_ts_filename(lang: str) -> str:
  return lang + '.ts'

def build_qm_filename(lang: str) -> str:
  return lang + '.qm'

def get_tool_qt_ver(name: str) -> int:
  out = subprocess.run([name, '-version'],
                       stdin=subprocess.DEVNULL,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL,
                       check=True, text=True)

  pattern = rf'{re.escape(name)} version (\d+)\.\d+\.\d+'
  match = re.match(pattern, out.stdout)
  if match is None:
    raise ValueError('REGEX pattern failed')

  ver_str = match.group(1)

  try:
    ver_int = int(ver_str)
  except ValueError as exc:
    raise ValueError('Is not an integer') from exc

  return ver_int

def chk_tool_qt_ver(tool: str, expected: int = QT_VER) -> (
  bool, typing.Optional[str]
):
  try:
    qt_ver = get_tool_qt_ver(tool)
  except subprocess.CalledProcessError as exc:
    return False, (f'Can\'t get version of {tool}, '
                   f'process exited with code {exc.returncode}')
  except UnicodeDecodeError:
    return False, f'Can\'t decode version output of {tool}'
  except ValueError as exc:
    return False, f'Can\'t parse version string of {tool}: {exc.args[0]}'
  except OSError as exc:
    return False, f'Can\'t run {tool} to get version: {exc.strerror}'

  if qt_ver != expected:
    return False, f'Tool {tool} isn\'t Qt {expected}, got {qt_ver}'

  return True, None

def chk_input_file(path: str) -> (bool, typing.Optional[str]):
  if not os.path.exists(path):
    return False, f'{path!r} doesn\'t exist'

  if not os.path.isfile(path):
    return False, f'{path!r} is a directory'

  if not os.access(path, os.R_OK):
    return False, f'{path!r} is not marked readable'

  return True, None

def main():
  parser = argparse.ArgumentParser(description='Localization tool')
  parser.add_argument('--update', '-u', action='store_true',
                      help='Add/remove string entries in translation '
                           '(.ts) files from program source files')
  parser.add_argument('--compile', '-c', action='store_true',
                      help='Make shippable locale (.qm) files out of .ts')
  args = parser.parse_args()

  if not args.update and not args.compile:
    print('Nothing to do, please pass an option flag',
          file=sys.stderr)
    sys.exit(0)

  work_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

  try:
    os.chdir(work_dir)
  except OSError as exc:
    print(f'Can\'t enter work dir {work_dir!r}: {exc.strerror}',
          file=sys.stderr)
    sys.exit(1)

  for tool in [
    LUPDATE,
    LRELEASE,
  ]:
    succeed, why = chk_tool_qt_ver(tool)
    if not succeed:
      print(why, file=sys.stderr)
      sys.exit(1)

  if args.update:
    for i, src in enumerate(SRCS):
      src_path = build_py_filename(src)
      succeed, why = chk_input_file(src_path)
      if not succeed:
        print(f'{why}; Was this file altered and you forgot?',
              file=sys.stderr)
        sys.exit(1)

      print(f'[{i + 1}/{len(SRCS)}] Syncing translation files '
            f'according to Python source file {src_path!r}',
            file=sys.stderr)

  if args.compile:
    for i, lang in enumerate(TRANSLATIONS):
      ts_path = build_ts_filename(lang)
      succeed, why = chk_input_file(ts_path)
      if not succeed:
        print(f'{why}; If you don\'t have this file, '
              'run a command to create it first',
              file=sys.stderr)
        sys.exit(1)

      print(f'[{i + 1}/{len(TRANSLATIONS)}] '
            f'Finalizing Qt locale file {ts_path!r}',
            file=sys.stderr)

  sys.exit(0)

if __name__ == '__main__':
  main()
