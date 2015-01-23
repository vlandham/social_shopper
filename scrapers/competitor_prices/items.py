import scrapy

class Product(scrapy.Item):
    
  source = scrapy.Field() # Retailer name, e.g. 'evo', 'rei'
  product_id = scrapy.Field()
  product_title = scrapy.Field()
  product_url = scrapy.Field()
  image_url = scrapy.Field()
  review_count = scrapy.Field()
  review_score = scrapy.Field()
  brand = scrapy.Field() 
  description_short = scrapy.Field()
  description_long = scrapy.Field()
  price = scrapy.Field() 
  price_low = scrapy.Field() 
  price_high = scrapy.Field()
  price_sale = scrapy.Field()
  image = scrapy.Field()
  condition = scrapy.Field()
  category = scrapy.Field()
  breadcrumbs = scrapy.Field() # unneeded? using just for nordstrom. 
  inventory = scrapy.Field()
