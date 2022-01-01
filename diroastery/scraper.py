import logging
import aiohttp
import asyncio

# from enum import Enum
from bs4 import BeautifulSoup

from . import coffee as co

class Scraper:
    def __init__(self):
        self.esp = 'https://diroastery.sk/kategoria-produktu/kava/espresso-kava/'
        self.fil = 'https://diroastery.sk/kategoria-produktu/kava/filter/'
        self.aut = 'https://diroastery.sk/kategoria-produktu/kava/automat-kava/'
        self.coffees = []

    async def scrapeEspresso(self):
        await self.scrapeMainData(self.esp, 'espresso')

    async def scrapeFilter(self):
        await self.scrapeMainData(self.esp, 'filter')

    async def scrapeAutomat(self):
        await self.scrapeMainData(self.esp, 'automat')

    async def scrapeMainData(self, link: str, ctype: str):

        logging.info('Scraping info from: {}, for coffee type: '.format(link, ctype))

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as r:
                soup = BeautifulSoup(await r.text(),'html.parser')

                items = soup.find_all("div", class_="astra-shop-summary-wrap" )

                await asyncio.gather(*[self.processMainElement(el, ctype) for el in items])

                await asyncio.gather(*[self.gatherCoffeeInfo(coffee) for coffee in self.coffees])

    async def gatherCoffeeInfo(self, coffee: co.Coffee):
        await coffee.scrapeCoffeeInfo()


    async def processMainElement(self, el, ctype: str):
        name = el.findChild("a").get_text(strip=True)
        logging.info('Processing coffee name: {}'.format(name))

        if (coffee := self.getCoffeeIfExists(name)) is None:
            coffee = co.Coffee()

            coffee.name = name
            coffee.link = el.findChild("a").get('href')
            coffee.price_low = el.findChildren("bdi")[0].get_text(strip=True)
            coffee.price_high = el.findChildren("bdi")[-1].get_text(strip=True)

            coffee.type.add(ctype)

            self.coffees.append(coffee)
        else:
            coffee.type.add(ctype)
            self.replaceCoffee(coffee)


    def getCoffeeIfExists(self, name: str) -> co.Coffee:
        try:
            c = [x for x in self.coffees if x.name == name][0]
        except IndexError:
            return None
        return c


    def replaceCoffee(self, coffee: co.Coffee):
        self.coffees = [ coffee if item.name == coffee.name else item for item in self.coffees ]






