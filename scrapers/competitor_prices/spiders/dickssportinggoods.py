# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy import log
import urlparse

from competitor_prices.items import Product


class DickssportinggoodsSpider(CrawlSpider):
  name = 'dickssportinggoods'
  allowed_domains = ['dickssportinggoods.com', 'http://www.dickssportinggoods.com', 'http://dickssportinggoods.com', 'www.dickssportinggoods.com', "dickssportinggoods.ugc.bazaarvoice.com", "http://dickssportinggoods.ugc.bazaarvoice.com"]
  start_urls = ['http://www.dickssportinggoods.com/products/brands-index.jsp']

  # rules = (
  #   Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
  # )

  def parse_start_url(self, response):
    top_brands = response.xpath("//li[@class='idxHeader']/a/@href").extract()
    sub_brands = response.xpath("//li[@class='idxBottomCat']/a/@href").extract()
    headers = response.xpath("//h2/a[@class='idxH2Link']/@href").extract()
    brands = top_brands + sub_brands + headers

    for brand in brands:
      # http://stackoverflow.com/questions/6499603/python-scrapy-convert-relative-paths-to-absolute-paths
      brand_url = urlparse.urljoin(response.url, brand.strip())
      yield scrapy.Request(url = brand_url, callback = self.parse_products_page)


  def parse_products_page(self, response):
    product_page_pattern = "//div[@class='prod-image']/a[contains(@href, 'product')]/@href"
    product_urls = response.xpath(product_page_pattern).extract()
    for product_url in product_urls:
      #product_url = str(self.base_url + product)
      self.log("Hitting product page: %s" % product_url)
      yield scrapy.Request(url = product_url, callback = self.parse_item)

    pagination_pattern = "//div[@class='pagination']/span[@class='pages']/a/@href"
    page_urls = response.xpath(pagination_pattern).extract()
    page_urls = set(page_urls)
    for page_url in page_urls:
      yield scrapy.Request(url = page_url, callback = self.parse_products_page)

  def parse_item(self, response):
    item = Product()
    item['product_title'] = response.xpath('//h1[@class="productHeading"]/text()').extract()[0].strip()
    price_string = response.xpath('//div[@id="imgDis"]/div[@class="op"]/text()').extract()[0].strip()
    if "to" in price_string:
      mprice = re.search("\$(\d+\.?\d*) to \$(\d+\.?\d*)", price_string)
      item['price_low'] = mprice.groups()[0]
      item['price_high'] = mprice.groups()[1]
    else:
      item['price'] = float(price_string.split(":")[1].strip().replace("$",""))

    parsed_url = urlparse.urlparse(response.url)
    item['product_id'] = urlparse.parse_qs(parsed_url.query)['productId'][0]
    item['product_url'] = response.url

    # Example of how to send data between requests. 
    # Here we put item in the 'meta' dict of the request. 
    # That way we can pull it back out inside parse_bazaar_html
    # WARNING: MAKE SURE THIS ROOT URL IS IN YOUR allowed_domains !!!!
    #  else, you will spend 2 hours debugging why the callback doesn't work
    bazaar_url = "http://dickssportinggoods.ugc.bazaarvoice.com/3020-en_us/{0}/reviews.djs?format=embeddedhtml".format(item['product_id'])
    request = scrapy.Request(url = bazaar_url, callback=self.parse_bazaar_html)
    request.meta['item'] = item

    yield request

  def parse_bazaar_html(self, response):
    '''
    This bazaarvoice response is actually just awful JS
    that emits HTML. If we could find another valid format then embeddedhtml
    that produced just JSON then we would have a lot better luck parsing it.

    Right now it uses ReEx's and I don't trust their success rate. 
    Also, check out: http://stackoverflow.com/questions/19021541/scrapy-scrapping-data-inside-a-javascript
    for more tips on scraping Ajax stuff.
    '''

    item = response.meta['item']
    #self.log("------------bazaar", level=log.DEBUG)

    mreview_count = re.search("Read (all)?.*?BVRRNumber.*?>(\d+).*?review",response.body)
    review_count = 0
    if mreview_count:
      if len(mreview_count.groups()) > 1:
        review_count = mreview_count.group(2)
      else:
        review_count = mreview_count.group(1)
    item['review_count'] = review_count

    mreview_score = re.search("BVRRRatingNumber.*?>(\d+\.?\d*).*?span",response.body)
    review_score = 0
    if mreview_score:
      review_score = mreview_score.group(1)
    item['review_score'] = review_score

    return item
