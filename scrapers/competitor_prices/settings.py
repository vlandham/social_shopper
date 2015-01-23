# Scrapy settings for competitor_prices project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'competitor_prices'

SPIDER_MODULES = ['competitor_prices.spiders']
NEWSPIDER_MODULE = 'competitor_prices.spiders'
USEDB = False # kill database for now
DATABASE = {'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432', 
            'username': 'erin',
            'password': 'root',
            'database': 'competitor_prices'}

#ITEM_PIPELINES = {'competitor_prices.pipelines.BackcountryPipeline': 0}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'competitor_prices (+http://www.yourdomain.com)'
