from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
import datetime

# from users.models import User
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

def do_alerts():
    logger.info("Do alerts()")

    alert_set = []

    # loop over all users and see if any of them have alerts, if so, pass the whole user portfolio list to them and be done with it.
    for u in User.objects.all():

        alert_set = []          ## Alert set is all the holdings for this user that have alerts behind them.
        
        logger.info("checking %s" % u)        
        
        for p in u.portfolio_set.all().order_by("name"):
            logger.info("Checking %s" % p)
            
            for h in p.holding_set.all().order_by("symbol__name"):

                logger.info("Checking %s" % h)
                
                if h.alert():
                    alert_set.append(h)

        if alert_set:
            logger.info("Sending Alert email")

            try:
                ctx = {"alert_set" : alert_set }
                message = render_to_string("alerter/email_report.html",ctx)
                mfrom = settings.EMAIL_HOST_USER

                send_mail(subject="Portfolio alerts", message="", html_message=message, from_email=mfrom, recipient_list=[u.email,])
            except:
                logger.info("error sending email")


class Command(BaseCommand):
    args = None
    help = "Generates and emails all stock alerts"
    
    def handle(self, *args, **options):

        # only send alerts during the week.
        loaddate = datetime.datetime.today()
        if loaddate.weekday() >= 0 and loaddate.weekday() < 5:
            do_alerts()
            
            