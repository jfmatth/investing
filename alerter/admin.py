from django.contrib import admin

# Register your models here.
from alerter.models import TradeAlert

class TradeAlertAdmin(admin.ModelAdmin):
    pass
admin.site.register(TradeAlert, TradeAlertAdmin)
