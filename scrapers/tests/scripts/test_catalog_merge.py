#py.test tests/scripts/test_catalog_merge.py -s

import unittest
import os
import pandas as pd
from scripts import match_products 

class MatcherTest(unittest.TestCase):
  def setUp(self):
    cur_dir = os.path.dirname(os.path.realpath(__file__))

  def test_is_matching_correctly(self):
    test_evo = pd.Series(['one', 'two', 'three'])
    test_bc = pd.Series(['one', 'three', 'four'])

    matcher = match_products.Matcher()
    results = matcher.is_match(test_evo, test_bc)

    self.assertEqual(len(results), 3)
    self.assertEqual(results, [True, False, True])
