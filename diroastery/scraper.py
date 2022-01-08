import aiohttp
import asyncio
import logging
import random
import unicodedata

# from enum import Enum
from bs4 import BeautifulSoup

COFFEE_TYPE_ESPRESSO='espresso'
COFFEE_TYPE_FILTER='filter'
COFFEE_TYPE_AUTOMAT='automat'
COFFEE_TYPE_OMNI='omni'

class Scraper:
    def __init__(self):
      self.link = 'https://diroastery.sk/kategoria-produktu/kava/'
      self.coffees = []

    async def scrapeCoffee(self):
      await self.scrapeMainData(self.link)

    async def scrapeMainData(self, link: str):

      logging.info('Scraping info from: {}'.format(link))

      async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
          soup = BeautifulSoup(await r.text(),'html.parser')

          items = soup.find_all("a", class_="ast-loop-product__link")

          await asyncio.gather(*[self.gatherCoffeeInfo(el.get('href')) for el in items])

    async def gatherCoffeeInfo(self, link: str):
      async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
          soup = BeautifulSoup(await r.text(),'html.parser')

          name = soup.findChild("h1", class_="entry-title").get_text(strip=True)

          # XXX: Hack we are not interested in sysdrip
          if 'Sydrip' in name:
            return

          logging.info('Scraping info for coffee {} from link {}'.format(name, link))

          if not (coffee := self.getCoffeeIfExists(name)):
            logging.info('Creating new item for coffee: {}'.format(name))

            coffee = {'name':'', 'link': '', 'price_low': '', 'price_high': '', 'type': set(), 'weight': set(),
                      'desc': '', 'img': ''}

            coffee['name'] = name
            coffee['link'] = link

            coffee['desc'] = unicodedata.normalize("NFKD", soup.find("div", class_="woocommerce-product-details__short-description").findChild("p").get_text(strip=True))
            coffee['img'] = soup.find("div", class_="woocommerce-product-gallery__image" ).findChild("a").attrs.get('href')

            items = soup.find_all("li", class_="button-variable-item")
            for el in items:
              val = el.findChild("span").get_text(strip=True)

              # if we got a match for 250g, 500g, 1000g
              if ('1000g' in val) or ('250g' in val) or ('500g' in val):
                coffee['weight'].add(val)
              elif ('Espresso' in val):
                coffee['type'].add(COFFEE_TYPE_ESPRESSO)
              elif ('Automat' in val):
                coffee['type'].add(COFFEE_TYPE_AUTOMAT)
              elif ('Filter' in val):
                coffee['type'].add(COFFEE_TYPE_FILTER)
              elif ('Omni' in val):
                coffee['type'].add(COFFEE_TYPE_OMNI)
              else:
                logging.debug("Found unmatchable child: {}".format(val))

            prices = soup.find_all("p", class_="price")
            for el in prices:
              coffee['price_low'] = el.findChildren("bdi")[0].get_text(strip=True)
              coffee['price_high'] = el.findChildren("bdi")[-1].get_text(strip=True)

            self.coffees.append(coffee)
          else:
            logging.info("Coffee item for name: {} was already scraped: \n {}".format(name, coffee))

    # Get random coffee from a list which has a type(espresso, filter, automat defined)
    def getRandomCoffee(self, ctype: str) -> dict:
      logging.info('Selecting random coffee with type: {}'.format(ctype))
      try:
        return random.choice([i for i in self.coffees if ctype in i['type']])
      except IndexError:
        return {}

    # Get instance of coffe from a list to update it and later replace
    def getCoffeeIfExists(self, name: str) -> dict:
      try:
        c = [x for x in self.coffees if x['name'] == name][0]
      except IndexError:
        return {}
      return c

    # Replace particular item in a list matching our criteria => name
    def replaceCoffee(self, coffee: dict):
      self.coffees = [ coffee if item['name'] == coffee['name'] else item for item in self.coffees ]

    def __str__(self):
      return unicodedata.normalize("NFKD", str(self.__dict__))

    def __repr__(self):
      return 'Scraper({})'.format(str(self.__dict__))

