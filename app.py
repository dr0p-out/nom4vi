#!/usr/bin/env python

import sys

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
                                 self.tr(
                                   'Exit application?\n'
                                   '\n'
                                   'Unsaved changes will be lost!\n'
                                 ),
                                 defaultButton=QMessageBox.StandardButton.No)
    if yesno == QMessageBox.StandardButton.Yes:
      self.__app.quit()

def main():
  app = QApplication(sys.argv)
  app.setApplicationName('Nôm4VI')

  parser = QCommandLineParser()
  parser.addHelpOption()
  parser.process(app)

  args = parser.positionalArguments()
  if len(args) > 0:
    print(app.tr(
            '%s: Too many positional arguments'
          ) % sys.argv[0],
          file=sys.stderr)
    sys.exit(1)

  tl = QTranslator()
  app.installTranslator(tl)

  ed = EditorWindow()
  ed.setEngine(QuocEngine())
  ed.show()

  keybinds = [
    keybind(app, ed) for keybind in (
      EndProgramKeyBind,
    )
  ]

  sys.exit(app.exec())

if __name__ == '__main__':
  main()
