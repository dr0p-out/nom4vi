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
  'ja_JP',
  'zh_CN',
]

SRCS: list[str] = [
  'kb_ui.py',
  'app.py',
]

APP_NAME = 'nom4vi'

def build_lupd_flags(inputs: list[str],
                     out_path: str,
                     target_language: str,
                     no_recursive: bool = True,
                     extensions: typing.Optional[list[str]] = None,
                     no_sort: bool = True,
                     no_obsolete: bool = True,
                     warnings_are_errors: bool = True) -> list[str]:
  res = [LUPDATE]
  if no_recursive:
    res.append('-no-recursive')
  if extensions is None:
    extensions = ['py']
  if len(extensions) > 0:
    res.extend(['-extensions', ','.join(extensions)])
  if no_sort:
    res.append('-no-sort')
  if no_obsolete:
    res.append('-no-obsolete')
  if warnings_are_errors:
    res.append('-warnings-are-errors')
  res.extend(['-target-language', target_language])
  res.extend(inputs)
  res.extend(['-ts', out_path])
  return res

def build_lrel_flags(inputs: list[str],
                     out_path: str,
                     no_unfinished: bool = True,
                     remove_identical: bool = True) -> list[str]:
  res = [LRELEASE]
  if no_unfinished:
    res.append('-nounfinished')
  if remove_identical:
    res.append('-removeidentical')
  res.extend(inputs)
  res.extend(['-qm', out_path])
  return res

def build_ts_filename(lang: str) -> str:
  return lang + '.ts'

def build_qm_filename(lang: str, prefix: str = APP_NAME) -> str:
  return f'{prefix}-{lang}.qm'

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
    return False, f'File {path!r} doesn\'t exist'

  if not os.path.isfile(path):
    return False, f'Path {path!r} is a directory'

  if not os.access(path, os.R_OK):
    return False, f'File {path!r} is not marked readable'

  return True, None

def fmt_cmd(args: list[str]) -> str:
  return ' '.join(repr(arg) for arg in args)

def run_cmd(args: list[str]) -> (bool, typing.Optional[str]):
  try:
    subprocess.run(args,
                   stdin=subprocess.DEVNULL,
                   check=True)
  except subprocess.CalledProcessError as exc:
    return False, f'Command {fmt_cmd(args)} failed with code {exc.returncode}'
  except OSError as exc:
    return False, f'Unable to invoke command {fmt_cmd(args)}: {exc.strerror}'

  return True, None

def get_mtime(path: str, strict: bool = False) -> (
  bool, typing.Optional[float], typing.Optional[str]
):
  try:
    val = os.stat(path).st_mtime
  except FileNotFoundError:
    if strict:
      return False, None, ('Can\'t get modifcation time of '
                           f'non-existing file {path!r}')
    val = float('NaN')
  except OSError as exc:
    return False, None, ('Can\'t get modification time of '
                         f'file {path!r}: {exc.strerror}')

  return True, val, None

def main():
  assert len(TRANSLATIONS) > 0 and len(SRCS) > 0, ('Language code or '
                                                   'source file list '
                                                   'is empty')

  parser = argparse.ArgumentParser(description='Localization tool')
  parser.add_argument('--update', '-u', action='store_true',
                      help='Add/remove string entries in translation '
                           '(.ts) files from program source files')
  parser.add_argument('--compile', '-c', action='store_true',
                      help='Make shippable locale (.qm) files out of .ts')
  args = parser.parse_args()

  should_upd = args.update
  should_build = args.compile
  if not should_upd and not should_build:
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

  for src in SRCS:
    succeed, why = chk_input_file(src)
    if not succeed:
      print(f'{why}; Was this file altered and you forgot?',
            file=sys.stderr)
      sys.exit(1)

  for lang in TRANSLATIONS:
    ts_path = build_ts_filename(lang)

    if should_upd:
      succeed, why = run_cmd(build_lupd_flags(SRCS, ts_path, lang))
      if not succeed:
        print(why, file=sys.stderr)
        sys.exit(1)

    if should_build:
      succeed, why = chk_input_file(ts_path)
      if not succeed:
        print(f'{why}; If you don\'t have this file, '
              'try to run a command to create it first',
              file=sys.stderr)
        sys.exit(1)

      qm_path = build_qm_filename(lang)

      succeed, qm_mtime, why = get_mtime(qm_path)
      if not succeed:
        print(why, file=sys.stderr)
        sys.exit(1)

      succeed, ts_mtime, why = get_mtime(ts_path)
      if not succeed:
        print(why, file=sys.stderr)
        sys.exit(1)

      if qm_mtime >= ts_mtime:
        continue

      succeed, why = run_cmd(build_lrel_flags([ts_path], qm_path))
      if not succeed:
        print(why, file=sys.stderr)
        sys.exit(1)

  sys.exit(0)

if __name__ == '__main__':
  main()
