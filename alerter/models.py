from django.db import models

from aim.models import Holding, HoldingAlert

# tradealert
# 
# Holds all email alerts that should go out to a user for each holding that is alerting.
class TradeAlert(models.Model):
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    alert = models.OneToOneField(HoldingAlert,
                                 blank=True, null=True,
                                 on_delete=models.DO_NOTHING,
                                )
    
    date = models.DateField()  # when did alert get added
    emailed = models.BooleanField(default=False)  # was it emailed


