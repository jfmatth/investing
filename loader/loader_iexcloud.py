# Moved to use signals instead of putting allthe code in a management file
import os

from django.db import transaction
from django.conf import settings

from aim.models import Symbol
from aim.models import Holding
from aim.models import Price

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


def LoadPricesForSymbol(sender, **kwargs):
    # loads the prices for a particular symbol
    logger.info("LoadPricesForSymbol")

    symbol = kwargs.get("symbol")
    history = "history" in kwargs

    if symbol:
        # symbol is an object from the ORM, no need to look it up.
        
        if history:
            logger.info(f"Downloading some history too")
        else:
            logger.info( f"Downloading prices for {symbol} ")

            quote = pyClient.quote(symbol.name)

            # quote has all the data we need, now find / create a price entry and save it. 
            # all dates are EPOCH, so need to divide by 1000 to get correct date.
            # also, Sandbox dates are 2+yrs in the future.
            # date   = models.DateField(db_index=True, blank=False)
            # high   = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
            # low    = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
            # close  = models.DecimalField(max_digits=12, decimal_places=3, blank=False)
            # volume = models.IntegerField(blank=False)
            



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

