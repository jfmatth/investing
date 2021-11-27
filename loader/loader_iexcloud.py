# Main code for loader, loading prices, Symbols, etc from source

# Moved to use signals instead of putting allthe code in management file

from django.db import transaction
import pyEX
import os

import logging
logger = logging.getLogger(__name__)


# def receiverLoadSymbols(sender, **kwargs):
#     print("received signal")


@transaction.atomic
 def receiverLoadSymbols(sender, **kwargs):
    logger.info("Main()")

    from aim.models import Symbol

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
    
    logger.info("Main() done")
    return True