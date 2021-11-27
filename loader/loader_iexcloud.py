# Moved to use signals instead of putting allthe code in a management file
import pyEX
import os

from django.db import transaction

from aim.models import Symbol
from aim.models import Holding
from aim.models import Price

import logging
logger = logging.getLogger(__name__)


@transaction.atomic
def LoadSymbols(sender, **kwargs):
    logger.info("LoadSymbols")

    environment = ""
    token = os.getenv("IEX_TOKEN", "None")

    if token[0]=="T":
        environment="sandbox"
    
    c = pyEX.Client(version=environment)

    logger.info(f"Retreiving symbols")
    symbols = c.symbols()

    logger.info(f"Updating DB...")
    for s in symbols:
        # rip through all the symbols and put them in our DB
        s, created = Symbol.objects.get_or_create(
                name=s['symbol'],
                defaults={"description": s['name'] }
                )

    logger.info(f"Loaded {len(symbols)} Symbols")
   
    logger.info("receiverLoadSymbols() done")

    return True


def LoadPricesForSymbol(sender, **kwargs):
    # loads the prices for a particular symbol
    logger.info("LoadPricesForSymbol")

    symbol = kwargs.get("symbol")
    history = "history" in kwargs

    if symbol:

        s = Symbol.objects.get(symbol)
        
        if history:
            print(f"Downloading some history too")
        else:
            print( f"Downloading prices for {symbol} ")

            



    else:
        print(f"Error - No symbol sent")

    return True


def LoadPricesForDay(sender, **kwargs):
    # loads the prices for all holdings for today
    logger.info("LoadPricesForDay")

    holdingList = Holding.objects.all().distinct()
    logger.info(f"There are {len(holdingList)} Holdings to pull down" )

    for h in holdingList:
        LoadPricesForSymbol(True, symbol=h.symbol )


    return True

