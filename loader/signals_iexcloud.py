# Moved to use signals instead of putting allthe code in a management file
import os

from django.db import transaction
from django.conf import settings

from aim.models import Symbol
from aim.models import Holding
from aim.models import Price

from datetime import date

import logging
logger = logging.getLogger(__name__)

# setup pyEX client with correct environment
import pyEX
# check the first character to see if it's T or not.
environment = ("sandbox" if settings.IEX_TOKEN[0] == "T" else "v1") 
pyClient = pyEX.Client(version=environment)

@transaction.atomic
def LoadSymbols(sender, **kwargs):
    logger.info("IEX LoadSymbols")

    logger.info(f"Retreiving symbols")
    symbols = pyClient.symbols()

    logger.info(f"Updating DB...")
    for s in symbols:
        # rip through all the symbols and put them in our DB
        s, created = Symbol.objects.get_or_create(
                name=s['symbol'],
                defaults={"description": s['name'] }
                )

    logger.info(f"Loaded {len(symbols)} Symbols")

    return True


# loads the prices for a particular symbol
def LoadPricesForSymbol(sender, **kwargs):
    logger.info("LoadPricesForSymbol")

    sObj = kwargs.get("symbol")

    if sObj:
        # lookup the symbol object from Symbols
        s = Symbol.objects.get(name=sObj)

        # symbol is a string
        logger.info( f"Downloading prices for {s} ")

        quote = pyClient.quote(s.name)

        sdate = quote['iexCloseTime']
        tdate = date.fromtimestamp(int(sdate)/1000)
        
        if not Price.objects.filter(symbol=s, date=tdate):

            p = Price()

            p.date = tdate
            p.symbol = s

            # account for when things are null
            p.high = (0 if quote['high'] ==None else quote['high'])
            p.low =  (0 if quote['low']  ==None else quote['low'])
            p.close = quote['iexClose']
            p.volume = quote['iexVolume']

            p.save()

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

