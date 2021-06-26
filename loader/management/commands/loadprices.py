from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.sites.models import Site

from django.db.utils import DataError

import logging
import csv
import datetime
from decimal import Decimal

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
from ftplib import FTP
from io import BytesIO

from aim.models import Symbol, Price, Split, Holding, Transaction
from loader.models import Exchange, ExchangePrice, PriceError, ExchangeSplit
from aim.models import transaction_types

# Get an instance of a logger
logger = logging.getLogger(__name__)

def EODDATA_loader(loaddate, history):
    """
    EODDATA_loader - this function downloads the latest exchange list for each list in Exchange(s), then downloads the prices
    for today into ExchangePrice.
        
    """

    # Make sure we have our environment variabels.
    if not settings.FTPLOGIN:
        logger.info("no FTPLOGIN in settings")
        return

    # Load todays prices from FTP EODDATA.com
    logger.info("EODDATA_loader() start")

    datestr = loaddate.strftime("%Y%m%d")
    logger.info("Getting ready to load Exchanges / Prices for %s" % datestr)

    ftp = FTP("ftp.eoddata.com")
    try:
        logger.info("FTP Login as %s" % settings.FTPLOGIN)
        ftp.login(settings.FTPLOGIN, settings.FTPPASS)
    except:
        logger.debug("Error logging into FTP")

    # loop over all Indexes, grabbing the latest exchange and then loading the prices we need.
    ftp.cwd("/Names")
    for e in Exchange.objects.all():
        mfile = BytesIO()

        try:
            exchangefile = "%s.txt" % e.name

            logger.info("Retreiving Exchange %s" % exchangefile)

            ftp.retrbinary("RETR %s" % exchangefile, mfile.write)

            e.data = mfile.getvalue()
            e.loaded = False
            e.save()

            logger.info("%s retrieved and saved" % exchangefile)

        except:
            logger.debug("Current datetime = $s, Error retreiving index %s" % (datetime.datetime.today(), e.name))

        del (mfile)

    # Get the splits for each exchange 
    logger.info("splits")
    ftp.cwd("/Splits")
    for x in Exchange.objects.all():
        mfile = BytesIO()
        # try:
        pricefile = "%s.txt" % (x.name)

        logger.info("Retreiving splits %s" % pricefile)

        ftp.retrbinary("RETR %s" % pricefile, mfile.write)

        p = ExchangeSplit(exchange=x, data=mfile.getvalue(), loaded=False )
        p.save()

        logger.info("%s Splits Saved" % pricefile)
        # except:
        #     logger.exception("error in splits")

        del (mfile)


    if history:
        ftp.cwd("/History")
    else:
        ftp.cwd("/")

    for e in Exchange.objects.all():
        mfile = BytesIO()
        try:
            pricefile = "%s_%s.txt" % (e.name, datestr)

            logger.debug("Retreiving splitsprices Exchange %s" % pricefile)

            ftp.retrbinary("RETR %s" % pricefile, mfile.write)
            logger.debug("got file")
            p = ExchangePrice(exchange=e, data=mfile.getvalue(), loaded=False)
            p.save()

            logger.debug("%s Prices Saved" % pricefile)
        except:
            logger.debug("error retreiving %s" % pricefile)

        del (mfile)

    logger.debug("ftp quit")
    ftp.quit()

    ftp = None
    mfile = None
    p = None

    logger.info("EODDATA_loader() complete")

@transaction.atomic
def ProcessExchange(f):
    """
    ProcessExchange - Given a string (typcically the text from EODDATA for an Exchange file, import them into the Symbols list )
    """

    start = datetime.datetime.now()

    logger.info("ProcessExchange() start %s" % start)

    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    header = reader.__next__()

    if not header[0] == "Symbol" or not header[1] == "Name":
        raise Exception("Error - Header line in %s looks wrong" % header)

    try:
        for csvline in reader:
            logger.debug("processing %s" % csvline)
            s, created = Symbol.objects.get_or_create(name=csvline[0], defaults={"description": csvline[1]})
            if created:
                logger.debug("Created %s" % s)
    except:
        logger.debug("Error loading %s" % csvline)

    logger.info("ProcessExchange() complete %s" % (datetime.datetime.now() - start) )


def LoadExchange():
    """
    LoadExchange - Gets all the records in Exchange that haven't been loaded, and process' them into the Symbols table.
    """
    logger.info("LoadExchange() start")

    count = 0

    for e in Exchange.objects.filter(loaded=False):
        # we have an exchange that hasn't been loaded.

        # sniff it out and load it into Symbols.
        # ProcessExchange(StringIO.StringIO(e.data))
        ProcessExchange(StringIO(e.data))

        e.loaded = True
        e.save()

        count += 1

    logger.info("LoadExchange() complete")

    return count


@transaction.atomic
def ProcessPrices(f, headers=False):
    """
    Given a string F, Import a file f into the prices table.
    """
    start = datetime.datetime.now()

    logger.info("ProcessPrices() start %s" % start)

    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if headers:
        header = reader.next()

        if not header[0] == "Symbol" or not header[1] == "Date":
            raise Exception("Error - Header line in looks wrong, %s" % header)

    # add import improvement. 
    datecheck = None
    count = 0

    logger.info("Start processing prices ...")
    for csvline in reader:

        d = datetime.datetime.strptime(csvline[1], "%Y%m%d").date()

        if not datecheck == d:
            # this is the date we are checking, so load all symbols from price for 
            # this date and use it for quick checking.
            logger.debug("datecheck = %s" % d)
            datecheck = d

            symbollist = set(Price.objects.filter(date=d).values_list("symbol__name", flat=True))
            logger.debug("sybollist populated")

        #   use the symbollist to verify each CSV line w/o a lookup
        if csvline[0] in symbollist:
            # if we already have it here, then skip.
            pass
        else:

            try:
                sym = Symbol.objects.get(name=csvline[0])
                p = Price()
                p.symbol = sym
                p.date = d
                p.high = csvline[3]
                p.low = csvline[4]
                p.close = csvline[5]
                p.volume = min(int(csvline[6]), 2147483647)
                p.save()

                count += 1

            except ObjectDoesNotExist:
                # add this to the price error if necessary
                p, c = PriceError.objects.get_or_create(symbolname=csvline[0])

    logger.info("ProcessPrices() complete %s" % (datetime.datetime.now() - start) )

    reader = None
    symbollist = None

    return count


@transaction.atomic
def ProcessSplits(f, headers=False):
    """
    Given a string F, Import into split records in the Split table
    """
    logger.info("ProcessSplits() start")

    count = 0

    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if headers:
        header = reader.__next__()

        if not header[0] == "Symbol" or not header[1] == "Date":
            raise Exception("Error - Header line looks wrong, %s" % header)

    logger.info("Start processing splits ...")
    for csvline in reader:
        try:
            sym = Symbol.objects.get(name=csvline[0])
            d = datetime.datetime.strptime(csvline[1], "%Y%m%d").date()
            r = csvline[2]

            s, created = Split.objects.get_or_create(symbol=sym, date=d, ratio=r)

            if created:
                count += 1

        except ObjectDoesNotExist:
            # add this to the price error if necessary
            p, c = PriceError.objects.get_or_create(symbolname=csvline[0])

    logger.info("ProcessSplits() complete")

    return count

def LoadPrices():
    """
    Gets all ExchangePrice records that haven't been loaded, and processes them.
    """
    logger.info("LoadPrices() start")

    count = 0

    for e in ExchangePrice.objects.filter(loaded=False):
        # we have an exchange that hasn't been loaded.

        # sniff it out and load it into Symbols.
        n = ProcessPrices(StringIO(e.data))
        e.loaded = True
        e.save()

        count += n

    logger.info("LoadPrices() complete")

    return count

def LoadSplits():
    """
    Gets all ExchangeSplit records that haven't been loaded, and processes them.
    """
    logger.info("LoadPrices() start")

    count = 0

    for s in ExchangeSplit.objects.filter(loaded=False):
        # we have an exchange that hasn't been loaded.

        # sniff it out and load it into Symbols.
        n = ProcessSplits(StringIO(s.data), headers=True)
        s.loaded = True
        s.save()

        count += n

    # # Since there is such overlap on splits, remove the ones that have been processed
    # ExchangeSplit.objects.filter(loaded=True).delete()

    logger.info("LoadPrices() complete")

    return count


def NotifyAdmin(subject, body):
    if not settings.EMAIL_HOST_USER:
        logger.info("NotifyAdmin - No EMAILHOST specified in settings")
        return

    mail_admins(subject, body)

@transaction.atomic
def AdjustForSplits():
    # go through all the aim.models.split records and adjust the price table and holdings for splits

    count = 0
    today = datetime.date.today()

    for s in Split.objects.filter(applied=False).filter(date__lte=today):

        logger.info("Split adjusting prices for  %s" % s.symbol)

        # ratios are in the format s1-s2 (for ex. 1-4 is one share for 4), so multiply
        # older prices by 4 to adjust to the new prices.
        s1 = int(s.ratio.split("-")[0])
        s2 = int(s.ratio.split("-")[1])

        price_multiplier =  Decimal( s2 / s1 )

        # First - Adjust the prices table
        # find all prices for this splits symbol and load them into a queryset
        # find the prices that less than the split date, and adust them
        for x in Price.objects.filter(symbol=s.symbol).filter(date__lt=s.date):
            x.high = x.high * price_multiplier
            x.low  = x.low * price_multiplier
            x.close = x.close * price_multiplier
            x.save()

        # adjust holdings prices if necessary
        if settings.SPLITS:

            transaction_multiplyer = Decimal( s1 / s2 )  # opposite of price_multiplier

            # Second - Find all holdings with this symbol that occured before the split and
            #          adjust how many shares they have
            for h in Holding.objects.filter(symbol=s.symbol):
                # if someone owns this holding, find all transactions that occured before the date
                # of the split

                logger.info("Working on Holding  %s" % h)

                for sh in h.transaction_set.filter(date__lt = s.date):
                    # so we have a transaciton that occured before the split, make sure we 
                    # add or subtract shares via a transaction into their account based on the 
                    # multiplier value

                    count += 1

                    if transaction_multiplyer > 1:
                        # we will buy some
                        t = Transaction()
                        t.holding = h 
                        t.date = s.date
                        t.shares =  (sh.shares * transaction_multiplyer) - sh.shares
                        t.price = 0                 # we are getting these for free
                        t.type = "Buy"
                        t.save()

                    elif transaction_multiplyer < 1:
                        # we will sell some
                        t = Transaction()
                        t.holding = h 
                        t.date = s.date
                        t.shares =  sh.shares - (sh.shares * transaction_multiplyer)
                        t.price = 0                 # we are selling these for nothing
                        t.type = "Sell"
                        t.save()
                        
                    else:
                        logger.debug("opps, no case for this?")

        
        s.applied = True
        s.save()

    return count


def LoadAll(date=None, history=False):
    """
    This runs through the daily routine to download the prices via FTP from EODDATA and then load them into the Symbol and Prices tables.
    """

    logger.info("LoadAll() Start")

    loaddate = date or datetime.datetime.today()

    if loaddate.weekday() >= 0 and loaddate.weekday() < 5:
        EODDATA_loader(loaddate, history)
        c1 = LoadExchange()
        c2 = LoadPrices()
        c3 = LoadSplits()
        c4 = AdjustForSplits()
        cs = Site.objects.get_current()

        subject = "%s - %s Prices Loaded for %s" % (cs.domain, cs.name, loaddate)
        body = "%s Exchanges, %s Prices loaded, %s Splits, %s Holdings adjusted" % (c1, c2, c3, c4)

        NotifyAdmin(subject, body)
    else:
        logger.info("Skipping weekend %s" % loaddate)

    logger.info("LoadAll() complete")



# turn this into a management command.
class Command(BaseCommand):
    args = "Date optional"
    help = "loads all stock prices for <date>"

    def handle(self, *args, **options):
        self.stdout.write("Loadprices.py - calling LoadAll()")
        LoadAll()
        self.stdout.write("Loadprices.py - Complete")
