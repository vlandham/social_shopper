import scrapy

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from competitor_prices.items import Product
from scrapy.contrib.linkextractors import LinkExtractor
import random

# For testing
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from ipdb import set_trace
# http://doc.scrapy.org/en/latest/topics/contracts.html
from scrapy.contracts import Contract
from scrapy.exceptions import ContractFail

class EvoSpider(CrawlSpider):
  name = 'evo'

  def __init__(self, *args, **kwargs):
    super(EvoSpider, self).__init__(*args, **kwargs)
    #self.allowed_domains = ['http://www.evo.com/', 'www.evo.com/']
    self.name = 'evo' 
    self.base_url = 'http://www.evo.com'
    self.start_urls = ['http://www.evo.com/brands.aspx']

  def parse_start_url(self, response):
    # Parse out the brand pages and return a new response object
    brands = response.xpath("//span[@class='col3']/a/@href").extract() 

    for brand in brands:
      brand_url = str(self.base_url + brand)
      yield scrapy.Request(url = brand_url, 
                           callback = self.parse_brand_landing_pages)
      self.log("Queued up: %s" % brand_url)

  def parse_brand_landing_pages(self, response):
    product_links = response.xpath("//div[@class='product']/a/@href").extract()

    for product in product_links:
      product_url = str(self.base_url + product)
      self.log("Here comes product: %s" % product_url)

      yield scrapy.Request(url = product_url, 
                           callback = self.parse_item)

    # Paginate!
    next_page = response.xpath("//div[@class='paging']/a[@class='inline-block next']/@href").extract()    

    if next_page:
      self.log("Found next page: %s" % next_page[0])
      link_butt = next_page[0].split('/')[-1]
      next_page_url = str(response.url.split('.aspx')[0] + "/" + link_butt)

      yield scrapy.Request(url = next_page_url,
                      callback = self.parse_brand_landing_pages)

  def parse_product_pages(self, response):
    product_page_pattern = "//a[contains(@class, 'qa-product-link')]/@href"
    product_pages = response.xpath(product_page_pattern).extract()

    for product in product_pages:
      product_url = str(self.base_url + product)
      self.log("Hitting product page: %s" % product_url)

      yield scrapy.Request(url = product_url,
                           callback = self.parse_item)

  def parse_item(self, response):

    item = Product()
    dirty_data = {}    

    dirty_data['source'] = [self.name]
    dirty_data['product_id'] = response.xpath("//span[@class='sku identifier']/span[@class='value']/text()").extract()
    dirty_data['review_count'] = response.xpath("//span[@class='review r0']/span[@class='rating']/span[@class='value-title']/@title").extract()
    dirty_data['review_score'] = response.xpath('//*[@id="pnlRightInformation"]/div[1]/span[1]/a/span[1]/span/@title').extract() 
    dirty_data['brand'] = response.xpath("//h1[@class='fn']/strong[@class='brand']/text()").extract() 
    dirty_data['description_short'] = response.xpath("//div[@id='detailsTab']/h2/text()").extract()
    dirty_data['description_long'] = [''.join(response.xpath("//div[@class='description']/text()").extract()).strip().replace('  ', ' ')]
    dirty_data['price'] = response.xpath("//div[@id='priceContainer']//span[@class='price']/text()").extract() 
    dirty_data['product_url'] = [response.url]
    dirty_data['image'] = response.xpath('//*[@id="ctl00_Body_mainImagePanel"]//img[@class="mainImage"]/@src').extract()
    dirty_data['condition'] = response.xpath('//*[@id="pnlRightInformation"]/div[1]/span[5]/text()').extract()

    for variable in dirty_data.keys():
      if dirty_data[variable]: 
        if variable == 'inventory':
          item[variable] = dirty_data[variable][0]
        elif variable in ['price', 'price_high', 'price_low', 'review_score']:
          item[variable] = float(dirty_data[variable][0].strip().replace('$', '').replace(',', ''))
        elif variable in ['review_count']: 
          item[variable] = int(dirty_data[variable][0].strip())
        elif variable == 'condition':
          item[variable] = dirty_data[variable][0].strip().replace('Condition: ', '') 
        else: 
          item[variable] = dirty_data[variable][0].strip()
    yield item
