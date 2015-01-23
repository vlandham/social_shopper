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


def to_float(extract):
  out = 0.0
  if len(extract) > 0:
    out = extract[0]
    out = out.replace("$","")
    out = out.replace(",", "")
    out = float(out)
  return out


class ReiSpider(CrawlSpider):
  name = 'rei'

  def __init__(self, *args, **kwargs):
    super(ReiSpider, self).__init__(*args, **kwargs)
    self.allowed_domains = ['http://www.rei.com/', 'www.rei.com']
    self.base_url = 'http://www.rei.com'
    self.start_urls = ['http://www.rei.com/brands']
    #self.rules = (
    #  Rule(LinkExtractor(restrict_xpaths = "//a[@class='qa-brand-link']/@href"), callback = "parse_start_url"),
    #  Rule(LinkExtractor(restrict_xpaths = "//a[@class='subcategory-link brand-plp-link qa-brand-plp-link']/@href")),
    #  Rule(LinkExtractor(restrict_xpaths = "//li[@class='pag-next']"), follow = True),
    #  Rule(LinkExtractor(restrict_xpaths = "//li[@class='pag-next']"), callback = "parse_product_page")
    #)

  def parse_start_url(self, response):
    # Parse out the brand pages and return a new response object
    # //*[@id="pageContent"]/div/div[3]  
    self.log("Parsing start url.")
    brands = response.xpath("//div[@class='brandGroup']//ul[@class=\"itemList\"]//@href").extract()

    for brand in brands:
      brand_url = str(self.base_url + brand)
      self.log("Queued up: %s" % brand_url)

      yield scrapy.Request(url = brand_url, 
                           callback = self.parse_brand_items_page)
  
  def parse_brand_items_page(self, response):
    brand_products_list = "//section[@class=\"search-result-set-1\"]//a[@class=\"productTileAnchor\"]//@href"
    product_list = response.xpath(brand_products_list).extract()

    for product in product_list:
      product_url = str(self.base_url + product)
      self.log("product_url is: %s" % product_url)
      yield scrapy.Request(url = product_url,
                      callback = self.parse_item)

    #check for pagination
    next_page = response.xpath("(//div[@class='searchPagination']/a[@data-ui='nextPage'])[1]//@href").extract()
    
    if next_page:
      self.log("Found next page: %s" % next_page[0])
      yield scrapy.Request(url = next_page[0],
                      callback = self.parse_brand_items_page)


  def handle_redirect(self, response):
    content = response.xpath("//noscript//meta/@content").extract()
    url_str = content[0].split(';')[1]
    real_url = str(self.base_url + url_str.split('=')[1])
    yield scrapy.Request(url = real_url,
                      callback = self.parse_item)


  def parse_item(self,response):
    
    item_name = response.xpath("//h1[@itemprop='name']/text()").extract()
    item_price = response.xpath("//li[@itemprop='price']/text()").extract()
    
    item = Product()

    #item['product_id'] = response.xpath("//b[@itemprop='productID']/text()").extract()[0]
    #item['review_count'] = to_float(response.xpath("//span[@class='review-count']/text()").extract())
    #item['review_score'] = to_float(response.xpath("//span[@itemprop='ratingValue']/text()").extract())
    item['brand'] = response.xpath("//head/meta[@name='brand']/@content" ).extract()
    item['description_short'] = response.xpath("//h1[@itemprop='name']/text()").extract()
    item['price'] = to_float(response.xpath("//li[@itemprop='price']/text()").extract())
    item['image'] =  response.xpath("//head/meta[@property='og:image']/@content" ).extract()
    #item['price_low'] = to_float(response.xpath("//span[contains(@class, 'qa-low-price')]/text()").extract())
    #item['price_high'] = to_float(response.xpath("//span[contains(@class, 'qa-high-price')]/text()").extract())
    item['product_url'] = response.url
    # self.log("item: %s" % item);

    yield item
     

   
