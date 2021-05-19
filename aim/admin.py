from django.contrib import admin

from aim.models import Portfolio

# Portfolio 
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'permission')
admin.site.register(Portfolio, PortfolioAdmin)

