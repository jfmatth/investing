# import datetime
# from decimal import Decimal
# import os

# from django.db import transaction
# from django.core.exceptions import ObjectDoesNotExist
# from django.conf import settings
# from django.core.mail import mail_admins
# from django.contrib.sites.models import Site
# from django.db.utils import DataError

# import pyEX

# # help fix encoding errors, django 1.x did automagically
# from django.utils.encoding import force_str

# # from aim.models import Symbol

# import logging
# logger = logging.getLogger(__name__)

# # from loader.models import Exchange, ExchangePrice, PriceError, ExchangeSplit
# # from aim.models import transaction_types

# def EODDATA_loader(loaddate, history):
#     """
#     EODDATA_loader - this function downloads the latest exchange list for each list in Exchange(s), then downloads the prices
#     for today into ExchangePrice.
        
#     """

#     # Make sure we have our environment variabels.
#     if not settings.FTPLOGIN:
#         logger.info("no FTPLOGIN in settings")
#         return

#     # Load todays prices from FTP EODDATA.com
#     logger.info("EODDATA_loader() start")

#     datestr = loaddate.strftime("%Y%m%d")
#     logger.info("Getting ready to load Exchanges / Prices for %s" % datestr)

#     ftp = FTP("ftp.eoddata.com")
#     try:
#         logger.info("FTP Login as %s" % settings.FTPLOGIN)
#         ftp.login(settings.FTPLOGIN, settings.FTPPASS)
#     except:
#         logger.debug("Error logging into FTP")

#     # loop over all Indexes, grabbing the latest exchange and then loading the prices we need.
#     ftp.cwd("/Names")
#     for e in Exchange.objects.all():
#         mfile = BytesIO()

#         try:
#             exchangefile = "%s.txt" % e.name

#             logger.info("Retreiving Exchange %s" % exchangefile)

#             ftp.retrbinary("RETR %s" % exchangefile, mfile.write)

#             e.data = force_str( mfile.getvalue() )
#             e.loaded = False
#             e.save()

#             logger.info("%s retrieved and saved" % exchangefile)

#         except:
#             logger.debug("Current datetime = $s, Error retreiving index %s" % (datetime.datetime.today(), e.name))

#         del (mfile)

#     # Get the splits for each exchange 
#     logger.info("splits")
#     ftp.cwd("/Splits")
#     for x in Exchange.objects.all():
#         mfile = BytesIO()
#         # try:
#         pricefile = "%s.txt" % (x.name)

#         logger.info("Retreiving splits %s" % pricefile)

#         ftp.retrbinary("RETR %s" % pricefile, mfile.write)

#         # p = ExchangeSplit(exchange=x, data=mfile.getvalue(), loaded=False )
#         p = ExchangeSplit(exchange=x, data=force_str(mfile.getvalue()), loaded=False )
#         p.save()

#         logger.info("%s Splits Saved" % pricefile)
#         # except:
#         #     logger.exception("error in splits")

#         del (mfile)


#     if history:
#         ftp.cwd("/History")
#     else:
#         ftp.cwd("/")

#     for e in Exchange.objects.all():
#         mfile = BytesIO()
#         try:
#             pricefile = "%s_%s.txt" % (e.name, datestr)

#             logger.debug("Retreiving splitsprices Exchange %s" % pricefile)

#             ftp.retrbinary("RETR %s" % pricefile, mfile.write)
#             logger.debug("got file")
#             # p = ExchangePrice(exchange=e, data=mfile.getvalue(), loaded=False)
#             p = ExchangePrice(exchange=e, data=force_str(mfile.getvalue()), loaded=False)
#             p.save()

#             logger.debug("%s Prices Saved" % pricefile)
#         except:
#             logger.debug("error retreiving %s" % pricefile)

#         del (mfile)

#     logger.debug("ftp quit")
#     ftp.quit()

#     ftp = None
#     mfile = None
#     p = None

#     logger.info("EODDATA_loader() complete")

# @transaction.atomic
# def ProcessExchange(f):
#     """
#     ProcessExchange - Given a string (typcically the text from EODDATA for an Exchange file, import them into the Symbols list )
#     """

#     start = datetime.datetime.now()

#     logger.info("ProcessExchange() start %s" % start)

#     dialect = csv.Sniffer().sniff(f.read(1024))
#     f.seek(0)
#     reader = csv.reader(f, dialect)

#     header = reader.__next__()

#     if not header[0] == "Symbol" or not header[1] == "Name":
#         raise Exception("Error - Header line in %s looks wrong" % header)

#     try:
#         for csvline in reader:
#             logger.debug("processing %s" % csvline)
#             s, created = Symbol.objects.get_or_create(name=csvline[0], defaults={"description": csvline[1]})
#             if created:
#                 logger.debug("Created %s" % s)
#     except:
#         logger.debug("Error loading %s" % csvline)

#     logger.info("ProcessExchange() complete %s" % (datetime.datetime.now() - start) )


# def LoadExchange():
#     """
#     LoadExchange - Gets all the records in Exchange that haven't been loaded, and process' them into the Symbols table.
#     """
#     logger.info("LoadExchange() start")

#     count = 0

#     for e in Exchange.objects.filter(loaded=False):
#         # we have an exchange that hasn't been loaded.

#         # sniff it out and load it into Symbols.
#         # ProcessExchange(StringIO.StringIO(e.data))
#         ProcessExchange(StringIO(e.data))

#         e.loaded = True
#         e.save()

#         count += 1

#     logger.info("LoadExchange() complete")

#     return count

# @transaction.atomic
# def Main():
#     logger.info("Main()")

#     environment = ""
#     token = os.getenv("IEX_TOKEN", "None")

#     if token[0]=="T":
#         environment="sandbox"
    
#     c = pyEX.Client(version=environment)

#     logger.info(f"Retreiving symbols")
#     symbols = c.symbols()

#     logger.info(f"Updating DB...")
#     for s in symbols:
#         # rip through all the symbols and put them in our DB
#         s, created = Symbol.objects.get_or_create(
#                 name=s['symbol'],
#                 defaults={"description": s['name'] }
#                 )

#     logger.info(f"Loaded {len(symbols)} Symbols")
    
#     logger.info("Main() done")
#     return 


from django.core.management.base import BaseCommand
from loader.signals import signalLoadSymbols, signalLoadPricesDay

class Command(BaseCommand):
    help = "loads all stock symbols from IEX_CLOUD"

    def handle(self, *args, **options):
        self.stdout.write("Management Command iexcloud Starting")

        signalLoadSymbols.send(True)
        signalLoadPricesDay(True)

        self.stdout.write("iexcloud Done")