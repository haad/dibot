import argparse
import asyncio
import logging
import json

from flask import Flask, request

from diroastery import db
from diroastery import scraper

from pprint import pprint

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)

@app.route("/")
def hello_world() -> str:
    return "<p>Your Coffee ordering Bot !</p>"

@app.route("/coffees")
async def getCoffees() -> str:
    s = await db.scrapeCoffeeDBinfo()
    return json.dumps(s.coffees, ensure_ascii=False, cls=SetEncoder)

@app.route("/random/")
async def getRandomCoffee() -> str:
    ctype = request.args.get('type', default = scraper.COFFEE_TYPE_ESPRESSO, type = str)
    s = await db.scrapeCoffeeDBinfo()

    logging.info('Get coffee info for type {}'.format(ctype))
    return json.dumps(s.getRandomCoffee(ctype), ensure_ascii=False, cls=SetEncoder)


async def main():
    logging.basicConfig(level=logging.INFO)

    #s = await db.scrapeCoffeeDBinfo()

    app.run()

if __name__ == "__main__":
    asyncio.run(main())
