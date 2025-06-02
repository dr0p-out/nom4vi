"""
keyboard UI implementations
"""

import typing

from PySide6.QtCore import (
  Qt,
  Signal,
  Slot,
)
from PySide6.QtGui import (
  QCloseEvent,
  QKeyEvent,
  QKeySequence,
  QShortcut,
  QWheelEvent,
)
from PySide6.QtWidgets import (
  QHBoxLayout,
  QLabel,
  QMessageBox,
  QPlainTextEdit,
  QPushButton,
  QStyle,
  QVBoxLayout,
  QWidget,
)

from engine_intf import BaseEngine

class InputArea(QPlainTextEdit):
  onDoLetter = Signal(str)
  onDoTransform = Signal(bool)
  onDoCommit = Signal()
  onDoBS = Signal()
  onDoDiscard = Signal()
  onDoToggleKeyboard = Signal()

  def __init__(self):
    QPlainTextEdit.__init__(self)
    self.setPlaceholderText(self.tr('Type here…'))
    self.__imePending = False

  def setImePending(self, v: bool):
    self.__imePending = v

  def keyPressEvent(self, ev: QKeyEvent):
    # make sure the special keys like Ctrl ain't currently held,
    # otherwise we want to use the default handlings instead
    modifiers = ev.modifiers()
    if modifiers == Qt.KeyboardModifier.NoModifier:
      k = ev.key()
      # always look at the letters
      if Qt.Key.Key_A <= k <= Qt.Key.Key_Z:
        self.onDoLetter.emit(ev.text())
        return
      if k == Qt.Key.Key_Tab:
        self.onDoToggleKeyboard.emit()
        return
      if self.__imePending:
        if k == Qt.Key.Key_Space:
          self.onDoTransform.emit(False)
          return
        if k == Qt.Key.Key_Return:
          self.onDoCommit.emit()
          return
        if k == Qt.Key.Key_Backspace:
          self.onDoBS.emit()
          return
        if k == Qt.Key.Key_Escape:
          self.onDoDiscard.emit()
          return
    elif modifiers == Qt.KeyboardModifier.ShiftModifier:
      k = ev.key()
      if Qt.Key.Key_A <= k <= Qt.Key.Key_Z:
        self.onDoLetter.emit(ev.text())
        return
      if self.__imePending:
        if k == Qt.Key.Key_Space:
          self.onDoTransform.emit(True)
          return

    # use the default handling of arrow keys, backspace, etc.
    QPlainTextEdit.keyPressEvent(self, ev)

  def wheelEvent(self, ev: QWheelEvent):
    if ev.modifiers() == Qt.KeyboardModifier.ControlModifier:
      delta = ev.angleDelta()
      if delta.x() == 0:
        dy = delta.y()
        if dy > 0:
          self.zoomIn()
          ev.accept()
          return
        if dy < 0:
          self.zoomOut()
          ev.accept()
          return
    QPlainTextEdit.wheelEvent(self, ev)

class EditorWindow(QWidget):
  """
  frontend wrapper for keyboard engines
  """

  def __init__(self):
    QWidget.__init__(self)
    layout = QVBoxLayout()
    self.setLayout(layout)

    bar = QWidget()
    layout.addWidget(bar)

    barLayout = QHBoxLayout()
    bar.setLayout(barLayout)

    reloadBtn = QPushButton()
    barLayout.addWidget(reloadBtn)
    reloadBtn.setText(self.tr('Reload'))
    reloadBtn.setEnabled(False)
    reloadBtn.clicked.connect(self.__handleReload)
    self.__reloadBtn = reloadBtn
    reloadIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)
    reloadBtn.setIcon(reloadIcon)

    keyReload = QShortcut(self)
    self.__keyReload = keyReload
    keyReload.setKey(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_R)
    keyReload.activated.connect(self.__handleReloadKey)

    saveBtn = QPushButton()
    barLayout.addWidget(saveBtn)
    saveBtn.setText(self.tr('Save'))
    saveBtn.setEnabled(False)
    saveBtn.clicked.connect(self.__handleSave)
    self.__saveBtn = saveBtn
    saveIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
    saveBtn.setIcon(saveIcon)

    keySave = QShortcut(self)
    self.__keySave = keySave
    keySave.setKey(QKeySequence.StandardKey.Save)
    keySave.activated.connect(self.__handleSaveKey)

    gotoBtn = QPushButton()
    barLayout.addWidget(gotoBtn)
    gotoBtn.setText(self.tr('Go-To…'))
    gotoBtn.setEnabled(False)
    gotoBtn.clicked.connect(self.__handleGoto)
    self.__gotoBtn = gotoBtn
    gotoIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward)
    gotoBtn.setIcon(gotoIcon)

    keyGoto = QShortcut(self)
    self.__keyGoto = keyGoto
    keyGoto.setKey(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_G)
    keyGoto.activated.connect(self.__handleGotoKey)

    helpBtn = QPushButton()
    barLayout.addWidget(helpBtn)
    helpBtn.setText(self.tr('Help'))
    helpBtn.clicked.connect(self.__handleHelp)
    helpIcon = self.style().standardPixmap(QStyle.StandardPixmap.SP_DialogHelpButton)
    helpBtn.setIcon(helpIcon)

    lbl = QLabel()
    layout.addWidget(lbl)
    self.__lbl = lbl
    lbl.setToolTip(self.tr('The current incomplete word '
                           'you\'ve inputted will be displayed at here.'))

    area = InputArea()
    layout.addWidget(area)
    area.onDoLetter.connect(self.__handleDoLetter)
    area.onDoTransform.connect(self.__handleTransform)
    area.onDoCommit.connect(self.__handleCommit)
    area.onDoBS.connect(self.__handleBS)
    area.onDoDiscard.connect(self.__handleDiscard)
    area.onDoToggleKeyboard.connect(self.__handleToggleKeyboard)
    font = area.font()
    font.setFamily('Nom Na Tong')
    area.setFont(font)
    self.__area = area
    area.setFocus()

    keyClose = QShortcut(self)
    self.__keyClose = keyClose
    keyClose.setKey(QKeySequence.StandardKey.Close)
    keyClose.activated.connect(self.__handleCloseKey)

    self.__engine: typing.Optional[BaseEngine] = None
    self.__keyboardEnabled = True

  def closeEvent(self, ev: QCloseEvent):
    yesno = QMessageBox.question(self, None,
                                 self.tr(
                                   'Leave window?\n'
                                   '\n'
                                   'Contents will not be saved.\n'
                                 ),
                                 defaultButton=QMessageBox.StandardButton.No)
    if yesno == QMessageBox.StandardButton.Yes:
      ev.accept()
      return
    ev.ignore()

  def setEngine(self, engine: typing.Optional[BaseEngine]):
    if engine is None:
      if self.__engine is not None:
        self.__engine.set_upd_buff_cb(None)
      self.__area.setImePending(False)
      if self.__keyboardEnabled:
        self.__lbl.setText('')
    else:
      engine.set_upd_buff_cb(self.__handleUpdateBuffer)
      # an engine should have already cleared its buffer
      # and informed us to clear our dirty UI states
    self.__engine = engine

  @Slot(str)
  def __handleDoLetter(self, c: str):
    if not self.__keyboardEnabled or self.__engine is None:
      self.__area.insertPlainText(c)
      return
    self.__engine.handle_letter(c)

  @Slot(bool)
  def __handleTransform(self, backwards: bool):
    pass

  @Slot()
  def __handleCommit(self):
    assert self.__engine is not None
    word = self.__engine.done()
    self.__area.insertPlainText(word)

  @Slot()
  def __handleBS(self):
    assert self.__engine is not None
    self.__engine.handle_bs()

  @Slot()
  def __handleDiscard(self):
    assert self.__engine is not None
    self.__engine.done()

  @Slot()
  def __handleToggleKeyboard(self):
    enabled = self.__keyboardEnabled
    if enabled:
      # we're in here if about to flip to disabled

      self.__area.setImePending(False)
      self.__lbl.setText(self.tr('<font color="red">• Keyboard Disabled</font>'))
      # engine state untouched
    else:
      # flipping to enabled

      if self.__engine is None:
        # no engine, never entered input state
        self.__lbl.setText('')
      else:
        # restore current state and buffer
        self.__area.setImePending(self.__engine.is_dirty())
        self.__lbl.setText(self.__engine.get_buff())
    self.__keyboardEnabled = not enabled

  def __handleUpdateBuffer(self, buff: str):
    self.__area.setImePending(buff != '')
    self.__lbl.setText(buff)

  @Slot()
  def __handleHelp(self):
    QMessageBox.information(self, None,
                            self.tr(
                              '<Tab>\t\t'             'Toggle keyboard ON/OFF\n'
                              '<Space>\t\t'           'Transform words\n'
                              '<Enter>\t\t'           'Commit word\n'
                              '<ESC>\t\t'             'Trash word buffer\n'
                              '\n'
                              '<{saveKeyRepr}>\t\t'   'Save into disk\n'
                              '<{gotoKeyRepr}>\t\t'   'Jump to line\n'
                              '<{reloadKeyRepr}>\t\t' 'Read again from file\n'
                              '<{closeKeyRepr}>\t\t'  'Close window\n'
                              '\n'
                              '(To type tiếng, say tieesng, not tieengs.)\n'
                            ).format(
                              saveKeyRepr=self.__keySave.key().toString(),
                              gotoKeyRepr=self.__keyGoto.key().toString(),
                              reloadKeyRepr=self.__keyReload.key().toString(),
                              closeKeyRepr=self.__keyClose.key().toString(),
                            ),
                            buttons=QMessageBox.StandardButton.Close)

  @Slot()
  def __handleReload(self):
    pass

  @Slot()
  def __handleReloadKey(self):
    self.__reloadBtn.animateClick()

  @Slot()
  def __handleSave(self):
    pass

  @Slot()
  def __handleSaveKey(self):
    self.__saveBtn.animateClick()

  @Slot()
  def __handleGoto(self):
    pass

  @Slot()
  def __handleGotoKey(self):
    self.__gotoBtn.animateClick()

  @Slot()
  def __handleCloseKey(self):
    self.close()
