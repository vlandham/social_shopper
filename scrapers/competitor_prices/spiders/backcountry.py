import scrapy

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from competitor_prices.items import Product
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import random

# For testing
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from ipdb import set_trace
# http://doc.scrapy.org/en/latest/topics/contracts.html
from scrapy.contracts import Contract
from scrapy.exceptions import ContractFail

class BackcountrySpider(CrawlSpider):
  name = 'backcountry'

  def __init__(self, *args, **kwargs):
    super(BackcountrySpider, self).__init__(*args, **kwargs)
    self.name = 'backcountry'
    self.allowed_domains = ['http://www.backcountry.com/', 'www.backcountry.com']
    self.base_url = 'http://www.backcountry.com'
    self.start_urls = ['http://www.backcountry.com/Store/catalog/shopAllBrands.jsp']

  def parse_start_url(self, response):
    # Start:  http://www.backcountry.com/Store/catalog/shopAllBrands.jsp
    brands = response.xpath("//a[@class='qa-brand-link']/@href").extract()

    for brand in brands:
      brand_url = str(self.base_url + brand)
      self.log("Queued up: %s" % brand_url)

      yield scrapy.Request(url = brand_url, 
                           callback = self.parse_brand_landing_pages)
    # End: http://www.backcountry.com/the-north-face
  
  def parse_brand_landing_pages(self, response):
    # Start: http://www.backcountry.com/the-north-face
    shop_all_pattern = "//a[@class='subcategory-link brand-plp-link qa-brand-plp-link']/@href"
    shop_all_link = response.xpath(shop_all_pattern).extract()

    if len(shop_all_link) > 1:
        self.log("Weird, found multiple 'shop all' links.")
        self.log(shop_all_link)

    if shop_all_link:
      all_product_url = str(self.base_url + shop_all_link[0])  

      yield scrapy.Request(url = all_product_url,
                           callback = self.parse_product_pages)
    else: 
      yield scrapy.Request(url = response.url,
                           callback = self.parse_product_pages)
    # End: http://www.backcountry.com/Store/catalog/brandLanding.jsp?brandId=88&show=all

  def parse_product_pages(self, response):
    # Start: http://www.backcountry.com/Store/catalog/brandLanding.jsp?brandId=88&show=all
    product_page_pattern = "//a[contains(@class, 'qa-product-link')]/@href"
    pagination_pattern = "//li[@class='page-link page-number']/a/@href"

    product_pages = response.xpath(product_page_pattern).extract()
    more_pages = response.xpath(pagination_pattern).extract()

    # Paginate!
    for page in more_pages:
      next_page = str(self.base_url + page)
      yield scrapy.Request(url = next_page,
                           callback = self.parse_product_pages)

    for product in product_pages:
      product_url = str(self.base_url + product)

      yield scrapy.Request(url = product_url,
                           callback = self.parse_item)
    # End: http://www.backcountry.com/the-north-face-half-dome-pullover-hooded-sweatshirt-womens

  def parse_item(self, response):

    item = Product()
    dirty_data = {}

    # Grab sku-level inventory
    skus = response.xpath("//input[@id='availability']/@value").extract()[0]
    skus = skus[1:-1] # remove first and last line
    products = [ sku.strip().split('=') for sku in skus.split(',') ]

    inventory = {} 
    for product in products:
      inventory.update({product[0]: int(product[1])})

    # Collect all the data, gotta catch 'em all!
    dirty_data['source'] = [self.name]
    dirty_data['product_id'] = response.xpath("//b[@itemprop='productID']/text()").extract()
    dirty_data['review_count'] = response.xpath("//span[@class='review-count']/text()").extract()
    dirty_data['review_score'] = response.xpath("//span[@itemprop='ratingValue']/text()").extract()
    dirty_data['brand'] = response.xpath("//span[@class='qa-brand-name']/text()").extract()
    dirty_data['description_short'] = [response.xpath("//h1[@itemprop='name']/text()").extract()[1].strip()]
    dirty_data['description_long'] = response.xpath("//div[@class='product-description']/text()").extract()
    dirty_data['price'] = response.xpath("//span[@itemprop='price']/text()").extract()
    dirty_data['price_low'] = response.xpath("//span[contains(@class, 'qa-low-price')]/text()").extract()
    dirty_data['price_high'] = response.xpath("//span[contains(@class, 'qa-high-price')]/text()").extract()
    dirty_data['product_url'] = [response.url]
    dirty_data['image'] = response.xpath("div[contains(@id, 'ui-main-product-image')]/@href").extract()
    dirty_data['inventory'] = [inventory]

    for variable in dirty_data.keys():
      if dirty_data[variable]: 
        if variable == 'inventory':
          item[variable] = dirty_data[variable][0]
        elif variable in ['price', 'price_low', 'price_high']:
          item[variable] = float(dirty_data[variable][0].strip().replace('$', '').replace(',', ''))
        elif variable in ['review_score', 'review_count']: 
          item[variable] = int(dirty_data[variable][0].strip())
        else: 
          item[variable] = dirty_data[variable][0].strip()

    yield item
