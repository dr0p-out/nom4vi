#!/usr/bin/env python

import unittest

from quoc import QuocEngine

class EngineTest(unittest.TestCase):
  def test_quoc(self):
    quoc = QuocEngine()
    quoc.handle_letter('N')
    quoc.handle_letter('o')
    quoc.handle_letter('o')
    quoc.handle_letter('m')
    self.assertEqual(quoc.done(), 'Nôm')

if __name__ == '__main__':
  unittest.main()
