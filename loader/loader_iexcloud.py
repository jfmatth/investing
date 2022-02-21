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
environment = ("sandbox" if settings.TOKEN[0] == "T" else "v1") 
pyClient = pyEX.Client(version=environment)

@transaction.atomic
def LoadSymbols(sender, **kwargs):
    logger.info("LoadSymbols")

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
   
    logger.info("receiverLoadSymbols() done")

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

        # quote has all the data we need, now find / create a price entry and save it. 
        # all dates are EPOCH, so need to divide by 1000 to get correct date.
        # also, Sandbox dates are 2+yrs in the future.
        # date   = models.DateField(db_index=True, blank=False)
        # high   = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
        # low    = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
        # close  = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
        # volume = models.IntegerField(blank=False)

        sdate = quote['iexCloseTime']
        tdate = date.fromtimestamp(int(sdate)/1000)
        print (f'date: {sdate} -> {tdate}')

        if not Price.objects.filter(symbol=s, date=tdate):

            p = Price()

            p.date = tdate
            p.symbol = s
            p.high = quote['high']
            p.low = quote['low']
            p.close = quote['iexClose']
            p.volume = quote['iexVolume']

            p.save()

            print(f"{p}")

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

