#!/usr/bin/env python

import sys

try:
  from PySide6.QtCore import (
    QCommandLineParser,
    QTranslator,
    Slot,
  )
  from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
  )
  from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QWidget,
  )
except ImportError:
  print('Can\'t import PySide6, is it installed?', file=sys.stderr)
  sys.exit(1)

from kb_ui import EditorWindow
from quoc import QuocEngine

class EndProgramKeyBind(QShortcut):
  def __init__(self, app: QApplication, parent: QWidget):
    QShortcut.__init__(self, parent)
    self.__app = app
    self.__parent = parent
    self.setKey(QKeySequence.StandardKey.Quit)
    self.activated.connect(self.__handleActivated)

  @Slot()
  def __handleActivated(self):
    yesno = QMessageBox.question(self.__parent, None,
                                 self.__app.translate(
                                   'EndProgramKeyBind',
                                   'Exit application?\n'
                                   '\n'
                                   'Unsaved changes will be lost!\n'
                                 ),
                                 defaultButton=QMessageBox.StandardButton.No)
    if yesno == QMessageBox.StandardButton.Yes:
      self.__app.quit()

def main():
  app = QApplication(sys.argv)

  tl = QTranslator()
  app.installTranslator(tl)

  app.setApplicationName(app.translate('main', 'Nôm4VI'))

  parser = QCommandLineParser()
  parser.setApplicationDescription(app.translate('main',
                                                 'Chữ Nôm workstation'))
  parser.addHelpOption()
  parser.process(app)

  args = parser.positionalArguments()
  if len(args) > 0:
    print(app.translate(
            'main',
            '%s: Too many positional arguments'
          ) % sys.argv[0],
          file=sys.stderr)
    sys.exit(1)

  ed = EditorWindow()
  ed.setEngine(QuocEngine())
  ed.show()

  keybinds: list[QShortcut] = [
    keybind(app, win) for keybind in (
      EndProgramKeyBind,
    ) for win in (
      ed,
    )
  ]

  sys.exit(app.exec())

if __name__ == '__main__':
  main()
