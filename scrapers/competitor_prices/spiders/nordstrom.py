# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from pprint import pprint
import urlparse

from competitor_prices.items import Product

def to_float(extract):
  out = 0.0
  if len(extract) > 0:
    out = extract[0]
    out = out.replace("$","")
    out = out.replace(",", "")
    out = float(out)
  return out

class NordstromSpider(CrawlSpider):
  name = 'nordstrom'
  allowed_domains = ['nordstrom.com', 'shop.nordstrom.com/', 'http://shop.nordstrom.com/']
  start_urls = ['http://shop.nordstrom.com/c/sitemap', 'http://shop.nordstrom.com/c/brands-list']

  # rules = (
  #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
  # )

  def parse_start_url(self, response):
    #category_links = response.xpath("//div[@class='column']/ul/li/a/@href").extract()
    links = response.xpath("//a[contains(@href, '/c/')]/@href").extract()
    for category_url in links:
      # http://stackoverflow.com/questions/6499603/python-scrapy-convert-relative-paths-to-absolute-paths
      # brand_url = urlparse.urljoin(response.url, brand.strip())
      yield scrapy.Request(url = category_url, callback = self.parse_products_page)

  def parse_products_page(self, response):
    product_page_pattern = "//a[@class='title']/@href"
    product_urls = response.xpath(product_page_pattern).extract()
    # self.log(pprint(product_urls))
    for product_id in product_urls:
      product_url = urlparse.urljoin(response.url, product_id.strip())

      # self.log("------------" + product_url, level=log.DEBUG)
      yield scrapy.Request(url = product_url, callback = self.parse_item)

    # pagination_pattern = "//div[@class='fashion-results-pager']/ul/li/a[@class='standard']/@href"
    # page_urls = response.xpath(pagination_pattern).extract()
    # for page_url in page_urls:
    #   yield scrapy.Request(url = page_url, callback = self.parse_products_page)

  def parse_item(self, response):
    item = Product()
    title = response.xpath("//section[@id='product-title']/h1/text()").extract()
    if len(title) == 0:
      title = response.xpath("//h1/text()").extract()

    item['product_title'] = title[0]
    new_product_id = response.xpath("//div[@class='item-number-wrapper']/text()").extract()
    if len(new_product_id) > 0:
      item['product_id'] = new_product_id[0].split("#")[1].strip()
    else:
      old_product_id = response.xpath("//td[@class='item-number']/text()").extract()
      if(len(old_product_id) > 0):
        old_product_id = old_product_id[0].split("#")[1].strip()
        item['product_id'] = old_product_id

    item['brand'] = response.xpath("//section[@id='brand-title']/h2/a/text()").extract()[0]

    sale_price = response.xpath("//span[contains(@class,'sale-price')]/text()").extract()
    if len(sale_price) > 0:
      sale_price = sale_price[0].replace("$","")
      sale_price = sale_price.split(":")[1].strip()
      item['price_sale'] = float(sale_price)

    price = response.xpath("//td[contains(@class,'item-price')]/span/text()").extract()
    if len(price) == 0:
      price = 0.0
    else:
      price = price[0]

    price = price.strip().replace("$","")
    price = price.replace(",","").strip()
    if "-" in price:
      prices = price.split("-")
      item['price_low'] = float(prices[0].strip())
      item['price_high'] = float(prices[1].strip())
    else:
      if ":" in price:
        price = price.split(":")[1]
      price = price.strip()
      if not price:
        price = 0.0
      item['price'] = float(price)
    breadcrumbs = response.xpath("//nav[@id='breadcrumb-nav']/ul/li/a/text()").extract()
    category = response.xpath("//nav[@id='breadcrumb-nav']/ul/li/text()").extract()
    breadcrumbs = breadcrumbs + category
    item['product_category'] = category[0]
    item['breadcrumbs'] = "-".join(breadcrumbs)
    item['product_url'] = response.url
    
    return item
