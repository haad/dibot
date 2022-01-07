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

class Scraper:
    def __init__(self):
        self.esp = 'https://diroastery.sk/kategoria-produktu/kava/espresso-kava/'
        self.fil = 'https://diroastery.sk/kategoria-produktu/kava/filter/'
        self.aut = 'https://diroastery.sk/kategoria-produktu/kava/automat-kava/'
        self.coffees = []

    async def scrapeEspresso(self):
        await self.scrapeMainData(self.esp, COFFEE_TYPE_ESPRESSO)

    async def scrapeFilter(self):
        await self.scrapeMainData(self.fil, COFFEE_TYPE_FILTER)

    async def scrapeAutomat(self):
        await self.scrapeMainData(self.aut, COFFEE_TYPE_AUTOMAT)

    async def scrapeMainData(self, link: str, ctype: str):

        logging.info('Scraping info from: {}, for coffee type: {}'.format(link, ctype))

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as r:
                soup = BeautifulSoup(await r.text(),'html.parser')

                items = soup.find_all("div", class_="astra-shop-summary-wrap" )

                await asyncio.gather(*[self.processMainElement(el, ctype) for el in items])
                await asyncio.gather(*[self.gatherCoffeeInfo(coffee) for coffee in self.coffees])

    async def gatherCoffeeInfo(self, coffee: dict):
        await self.scrapeCoffeeInfo(coffee)

    async def processMainElement(self, el, ctype: str):
        name = el.findChild("a").get_text(strip=True)
        logging.info('Processing coffee name: {}'.format(name))

        if not (coffee := self.getCoffeeIfExists(name)):
            coffee = {'name':'', 'link': '', 'price_low': '', 'price_high': '', 'type': set(), 'desc': '', 'img': ''}

            coffee['name'] = name
            coffee['link'] = el.findChild("a").get('href')
            coffee['price_low'] = el.findChildren("bdi")[0].get_text(strip=True)
            coffee['price_high'] = el.findChildren("bdi")[-1].get_text(strip=True)

            coffee['type'].add(ctype)

            self.coffees.append(coffee)
        else:
            coffee['type'].add(ctype)
            self.replaceCoffee(coffee)


    async def scrapeCoffeeInfo(self, coffee):
      async with aiohttp.ClientSession() as session:
        async with session.get(coffee.get('link')) as r:
          soup = BeautifulSoup(await r.text(),'html.parser')

          logging.info('Scraping info for coffee {} from link {}'.format(coffee.get('name'), coffee.get('link')))

          coffee['desc'] = unicodedata.normalize("NFKD", soup.find("div", class_="woocommerce-product-details__short-description" ).findChild("p").get_text(strip=True))
          coffee['img'] = soup.find("div", class_="woocommerce-product-gallery__image" ).findChild("a").attrs.get('href')

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





