from django.views.generic import ListView
from aim.models import Symbol

from datetime import timedelta, date

DAYS_5YRS = 365 * 5

# Create your views here.
class graphview(ListView):
    template_name = "graphview.html"  # so normally this would be in the app/templates folder, but django is looking in AIM, lame, so 
    # i put it there :(

    def get_queryset(self):
        td = timedelta(days=DAYS_5YRS)
        d = date.today() - td
#        return Symbol.objects.get(name=self.kwargs['symbol']).price_set.order_by('date')
        return Symbol.objects.get(name=self.kwargs['symbol']).price_set.filter(date__gte=d).order_by('date')

# class testgraphview(ListView):
#     template_name = "graphs/testgraph.html"

#     def get_context_data(self, **kwargs):
#         cd = super(testgraphview, self).get_context_data(**kwargs)

#         cd['symbol'] = self.kwargs['symbol']
#         return cd

#     def get_queryset(self):
#         return Symbol.objects.get(name=self.kwargs['symbol']).price_set.all()

