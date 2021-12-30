import logging
import requests

# from enum import Enum
from bs4 import BeautifulSoup

from . import coffee as co

class Scraper:
    def __init__(self):
        self.esp = 'https://diroastery.sk/kategoria-produktu/kava/espresso-kava/'
        self.fil = 'https://diroastery.sk/kategoria-produktu/kava/filter/'
        self.aut = 'https://diroastery.sk/kategoria-produktu/kava/automat-kava/'
        self.coffees = []

    def scrapeEspresso(self):
        self.scrapeMainData(self.esp, 'espresso')

    def scrapeFilter(self):
        self.scrapeMainData(self.esp, 'filter')

    def scrapeAutomat(self):
        self.scrapeMainData(self.esp, 'automat')

    def scrapeMainData(self, link, ctype):

        logging.info('Scraping info from: {}, for coffee type: '.format(link, ctype))

        r = requests.get(link)

        soup = BeautifulSoup(r.text,'html.parser')

        items = soup.find_all("div", class_="astra-shop-summary-wrap" )

        for el in items:
            name = el.findChild("a").get_text(strip=True)
            logging.info('Processing coffee name: {}'.format(name))


            if (coffee := self.getCoffeeIfExists(name)) is None:
                coffee = co.Coffee()

                coffee.name = name
                coffee.link = el.findChild("a").get('href')
                coffee.price_low = el.findChildren("bdi")[0].get_text(strip=True)
                coffee.price_high = el.findChildren("bdi")[-1].get_text(strip=True)

                coffee.type.add(ctype)

                coffee.scrapeCoffeeInfo()

                self.coffees.append(coffee)
            else:
                coffee.type.add(ctype)
                self.replaceCoffee(coffee)


    def getCoffeeIfExists(self, name):
        try:
            c = [x for x in self.coffees if x.name == name][0]
        except IndexError:
            return None
        return c


    def replaceCoffee(self, coffee):
        self.coffees = [ coffee if item.name == coffee.name else item for item in self.coffees ]






