import unittest
import os
from scripts import dedup_products

class DedupProductsTest(unittest.TestCase):
  def setUp(self):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    self.start_file = os.path.join(cur_dir, "mocks/startfile.jsonlines")
    self.end_file = os.path.join(cur_dir, "mocks/endfile.jsonlines")

  def test_it_can_dedup_products(self):
    deduper = dedup_products.Deduper()
    events = deduper.run(self.start_file, self.end_file)
    self.assertGreater(len(events), 4)
    new_product_events = [e for e in events if e["event"] == "new_product"]
    self.assertEqual(len(new_product_events), 1)
    price_change_events = [e for e in events if (e["event"] == "change" and e["attr"] == "price")]
    self.assertEqual(len(price_change_events), 1)

  def test_it_can_parce_dates(self):
    deduper = dedup_products.Deduper()
    date = deduper.get_date("bla/bla/bla/a_file_is_named_2014_07_03.jsonlines")
    self.assertEqual(date, "2014_07_03")


