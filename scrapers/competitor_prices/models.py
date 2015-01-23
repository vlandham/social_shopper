from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

DeclarativeBase = declarative_base()

def create_competitor_prices_table(engine):
  DeclarativeBase.metadata.create_all(engine)

def db_connect():
  """ 
    Performs database connection using settings from settings.py.
    Returns sqlalchemy engine instance.
  """
  return create_engine(URL(**settings.DATABASE))

class CompetitorPrices(DeclarativeBase):
  """ 
    sqlalchemy competitor_prices model 
  """

  __tablename__ = "competitor_prices"

  product_id = Column(Integer, primary_key = True)
  product_name = Column('product_name', String, nullable = True)
  brand = Column('brand', String, nullable = True)
  price_high = Column('price_high', Numeric(10, 2), nullable = True)
  price_low = Column('price_low', Numeric(10, 2), nullable = True)
