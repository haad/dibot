import argparse
import asyncio
import logging
import os
import pickle
import time

from diroastery import scraper
from diroastery import coffee

from pprint import pprint

COFFEE_DB = '/tmp/coffee.db'

def dumpCoffeeDB(file, coffees):
    pickle.dump(coffees, open(file, "wb" ))


def loadCoffeeDB(file) -> list:
    return pickle.load(open(file, "rb" ))

def checkCoffeeDBtimestamp(file) -> bool:
    return (round(time.time() - os.stat(file).st_mtime) / 60 < 1) and (False)

async def main():
    logging.basicConfig(level=logging.INFO)

    start_time = time.time()
    s = scraper.Scraper()

    if checkCoffeeDBtimestamp(COFFEE_DB):
        logging.info('Loading coffeeDB from disk...')
        s.coffees = loadCoffeeDB(COFFEE_DB)
    else:
        logging.info('Updating scraped coffees...')
        await s.scrapeEspresso()
        await s.scrapeFilter()

    logging.info('--- Scraping took: {} seconds ---'.format(time.time() - start_time))

    print(s.coffees)

    dumpCoffeeDB(COFFEE_DB, s.coffees)

if __name__ == "__main__":
    asyncio.run(main())
