import unittest
from competitor_prices.spiders import dickssportinggoods
from responses import fake_response_from_file
from scrapy.http import Response, Request, HtmlResponse
from pprint import pprint
import urlparse

class DicksSpiderTest(unittest.TestCase):
  def setUp(self):
    self.spider = dickssportinggoods.DickssportinggoodsSpider()


  def _test_item_results(self, results, expected_length):
    count = 0
    permalinks = set()
    for result in results:
      count += 1
      item = result
      # The Dicks spider makes an additional request to
      # get the comments from bazaarvoice - so we need
      # to pull out the item from the request first
      if isinstance(result, Request):
        item = result.meta['item']
      self.assertIsNotNone(item['product_id'])
      self.assertIsNotNone(item['price'])
    self.assertEqual(count, expected_length)

  def test_it_can_parse_product_page(self):
    results = self.spider.parse_item(fake_response_from_file('dickssportinggoods/gazelle.html', 'http://www.dickssportinggoods.com/product/index.jsp?productId=24600616'))

    self._test_item_results(results, 1)

  def test_it_can_parse_starting_page(self):
    results = self.spider.parse_start_url(fake_response_from_file('dickssportinggoods/brands.html', 'http://www.dickssportinggoods.com/products/brands-index.jsp'))
    count = 0
    for request in results:
      self.assertEqual(request.method, "GET")
      parsed_url = urlparse.urlparse(request.url)
      # ensure they are all products links
      self.assertIn("products", parsed_url.path)
      count += 1
    #   pprint(request)
    # I don't know if i should have an exact number here
    # Ensuring some minimum seems fine.
    self.assertGreater(count, 2000)

