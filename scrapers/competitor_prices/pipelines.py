# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from models import CompetitorPrices, db_connect, create_competitor_prices_table 

from pprint import pprint

class BackcountryPipeline(object):
  """ 
    Pipeline for scraped competitor prices.
  """
  def __init__(self, use_database):
    self.use_database = use_database
    if not use_database:
      pass
    else:
      engine = db_connect()
      create_competitor_prices_table(engine)
      self.Session = sessionmaker(bind = engine)

  @classmethod
  def from_crawler(cls, crawler):
    settings = crawler.settings
    use_db = settings.get("USEDB", False)
    if (isinstance(use_db, basestring)) and (use_db.lower == 'true'):
      use_db = True

    return cls(use_db)
  

  def save_to_database(self, item):
    session = self.Session()
    price = CompetitorPrices(**item)

    try:
      session.add(price)
      session.commit()
    except:
      # Rollback if something gets fucked.
      session.rollback()
      raise
    finally:
      session.close()

  def process_item(self, item, spider):
    """
    """
    if self.use_database:
      self.save_to_database(item)
    return item


