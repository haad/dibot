import argparse
import asyncio
import pickle
import logging
import os
import time

from . import scraper

COFFEE_DB_PATH = '/tmp/coffee.db'
COFFEE_DB_REFRESH_INTERVAL = 60 #in seconds

def dumpCoffeeDB(file: str, coffees: list):
    pickle.dump(coffees, open(file, "wb" ))

def loadCoffeeDB(file: str) -> list:
    return pickle.load(open(file, "rb" ))

def checkCoffeeDBtimestamp(file: str) -> bool:
    try:
        return (round(time.time() - os.stat(file).st_mtime) < COFFEE_DB_REFRESH_INTERVAL)
    except FileNotFoundError:
        return False

async def scrapeCoffeeDBinfo() -> scraper.Scraper:
    start_time = time.time()
    s = scraper.Scraper()

    if checkCoffeeDBtimestamp(COFFEE_DB_PATH):
        logging.info('Loading coffeeDB from disk...')
        s.coffees = loadCoffeeDB(COFFEE_DB_PATH)
    else:
        logging.info('Updating scraped coffees...')
        await s.scrapeCoffee()

    logging.info('--- Scraping took: {} seconds ---'.format(round(time.time() - start_time, 4)))

    dumpCoffeeDB(COFFEE_DB_PATH, s.coffees)

    return s
