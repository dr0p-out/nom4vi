import abc
import dataclasses
import typing

@dataclasses.dataclass
class TransformResultItem:
  # could be romanized word or language-specific spellings
  fully_qualified_spelling: str

  out_word: str

  freq: float

class BaseEngine(abc.ABC):
  UPD_BUFF_CB_TYPE = typing.Callable[[str], None]

  @abc.abstractmethod
  def handle_letter(self, c: str):
    """
    put the letter into buffer, and do whatever processing if needed
    """

  @abc.abstractmethod
  def handle_bs(self):
    """
    undo the last letter and update the buffer

    for simplest case this could means removing the last letter from buffer
    """

  @abc.abstractmethod
  def set_upd_buff_cb(self, fn: typing.Optional[UPD_BUFF_CB_TYPE]):
    """
    set a callback function that is called whenever the underlying buffer updates

    note, a buffer clear and callback will be triggered immediately
    """

  @abc.abstractmethod
  def done(self) -> str:
    """
    get current buffer and clear it
    """

  def get_trs(self) -> list[TransformResultItem]:
    return []

  @abc.abstractmethod
  def get_buff(self) -> str:
    ...

  @abc.abstractmethod
  def is_dirty(self) -> bool:
    ...
