"""
Chữ Quốc ngữ support
"""

import typing
import string

from engine_intf import BaseEngine

EXTRA_ALPHAS: dict[str, str] = {
  'a': 'â',
  'd': 'đ',
  'e': 'ê',
  'o': 'ô',
}

MODIFIER_EXTRA_ALPHA2 = 'w'

EXTRA_ALPHAS2: dict[str, str] = {
  'a': 'ă',
  'o': 'ơ',
  'u': 'ư',
}

MODIFIER_TONE1 = 'f'

TONE1: dict[str, str] = {
  'a': 'à',
  'ă': 'ằ',
  'â': 'ầ',
  'e': 'è',
  'ê': 'ề',
  'i': 'ì',
  'o': 'ò',
  'ô': 'ồ',
  'ơ': 'ờ',
  'u': 'ù',
  'ư': 'ừ',
  'y': 'ỳ',
}

MODIFIER_TONE2 = 'r'

TONE2: dict[str, str] = {
  'a': 'ả',
  'ă': 'ẳ',
  'â': 'ẩ',
  'e': 'ẻ',
  'ê': 'ể',
  'i': 'ỉ',
  'o': 'ỏ',
  'ô': 'ổ',
  'ơ': 'ở',
  'u': 'ủ',
  'ư': 'ử',
  'y': 'ỷ',
}

MODIFIER_TONE3 = 'x'

TONE3: dict[str, str] = {
  'a': 'ã',
  'ă': 'ẵ',
  'â': 'ẫ',
  'e': 'ẽ',
  'ê': 'ễ',
  'i': 'ĩ',
  'o': 'õ',
  'ô': 'ỗ',
  'ơ': 'ỡ',
  'u': 'ũ',
  'ư': 'ữ',
  'y': 'ỹ',
}

MODIFIER_TONE4 = 's'

TONE4: dict[str, str] = {
  'a': 'á',
  'ă': 'ắ',
  'â': 'ấ',
  'e': 'é',
  'ê': 'ế',
  'i': 'í',
  'o': 'ó',
  'ô': 'ố',
  'ơ': 'ớ',
  'u': 'ú',
  'ư': 'ứ',
  'y': 'ý',
}

MODIFIER_TONE5 = 'j'

TONE5: dict[str, str] = {
  'a': 'ạ',
  'ă': 'ặ',
  'â': 'ậ',
  'e': 'ẹ',
  'ê': 'ệ',
  'i': 'ị',
  'o': 'ọ',
  'ô': 'ộ',
  'ơ': 'ợ',
  'u': 'ụ',
  'ư': 'ự',
  'y': 'ỵ',
}

class QuocEngine(BaseEngine):
  """
  implements a simple TELEX keyboard
  """

  def __init__(self):
    BaseEngine.__init__(self)
    self.__buff: list[str] = []
    self.__upd_buff_cb: typing.Optional[BaseEngine.UPD_BUFF_CB_TYPE] = None

  def __buff_to_str(self):
    return ''.join(self.__buff)

  def __notify_buff_watcher(self, word: typing.Optional[str] = None):
    if self.__upd_buff_cb is not None:
      if word is None:
        word = self.__buff_to_str()
      self.__upd_buff_cb(word)

  def __is_buff_empty(self) -> bool:
    return len(self.__buff) == 0

  def handle_letter(self, c: str):
    if c not in string.ascii_letters:
      raise ValueError(f'{c!r} is not an letter')
    if self.__is_buff_empty():
      # nothing to do for the first char
      self.__buff.append(c)
    else:
      # handle TELEX sequences if detected

      last_char = self.__buff[-1]
      last_char_lower = last_char.lower()
      c_lower = c.lower()
      last_char_is_upper = last_char.isupper()
      for k, arr in (
        (last_char_lower, EXTRA_ALPHAS),
        (MODIFIER_EXTRA_ALPHA2, EXTRA_ALPHAS2),
        (MODIFIER_TONE1, TONE1),
        (MODIFIER_TONE2, TONE2),
        (MODIFIER_TONE3, TONE3),
        (MODIFIER_TONE4, TONE4),
        (MODIFIER_TONE5, TONE5),
      ):
        if c_lower == k:
          if last_char_lower in arr:
            new = arr[last_char_lower]
            if last_char_is_upper:
              new = new.upper()
            self.__buff[-1] = new
          else:
            self.__buff.append(c)
          break
      else:
        self.__buff.append(c)
    self.__notify_buff_watcher()

  def handle_bs(self):
    if self.__is_buff_empty():
      return
    self.__buff.pop()
    self.__notify_buff_watcher()

  def set_upd_buff_cb(self,
                      fn: typing.Optional[BaseEngine.UPD_BUFF_CB_TYPE]):
    self.__upd_buff_cb = fn
    if fn is None:
      return
    # doesn't really make sense for a new
    # watcher to start with a dirty buffer anyways
    self.__buff.clear()
    self.__notify_buff_watcher()

  def done(self) -> str:
    if self.__is_buff_empty():
      return ''
    word = self.__buff_to_str()
    self.__buff.clear()
    self.__notify_buff_watcher('')
    return word

  def get_buff(self) -> str:
    return self.__buff_to_str()

  def is_dirty(self) -> bool:
    return not self.__is_buff_empty()
