__author__ = 'jfmatth'

from optparse import make_option
import datetime

from django.core.management.base import BaseCommand
from .loadprices import LoadAll

from aim.daterange import Daterange

import logging

logger = logging.getLogger(__name__)

# turn this into a management command.
class Command(BaseCommand):
    args = "Date optional"
    help = "loads all stock prices for <date>"

    def add_arguments(self, parser):
        parser.add_argument('start', nargs='+', type=str)

    def handle(self, *args, **options):
        sd = ed = None

        sd = datetime.datetime.strptime(options['start'][0], "%Y-%m-%d").date()
        ed = datetime.date.today()

        print(sd,ed)

        for x in Daterange(sd, ed):

            if (datetime.date.today() - x).days > 7:
                h = True
            else:
                h = False

            print ("Loading {0}".format(x) )
            LoadAll(date=x, history=h)