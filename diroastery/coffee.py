# class CoffeeType(Enum):
#     Espresso=1
#     Filter=2
#     Automat=3

import requests
import logging
import unicodedata
import aiohttp


# from enum import Enum
from bs4 import BeautifulSoup

class Coffee(dict):
    def __init__(self):
      self.name = ''
      self.link = ''
      self.type = set()

      self.img  = ''
      self.desc = ''

      self.price_high = ''
      self.price_low = ''

      self.metadata = {}

    async def scrapeCoffeeInfo(self):
      async with aiohttp.ClientSession() as session:
        async with session.get(self.link) as r:
          soup = BeautifulSoup(await r.text(),'html.parser')

          logging.info('Scraping info for coffee {} from link {}'.format(self.name, self.link))

          self.desc = unicodedata.normalize("NFKD", soup.find("div", class_="woocommerce-product-details__short-description" ).findChild("p").get_text(strip=True))
          self.img = soup.find("div", class_="woocommerce-product-gallery__image" ).findChild("a").attrs.get('href')


    def __str__(self):
      return str(self.__dict__)

    def __repr__(self):
      return 'Coffee({})'.format(str(self.__dict__))
