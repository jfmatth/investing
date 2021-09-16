from django.shortcuts import render
from django.views.generic import ListView, TemplateView, UpdateView, CreateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from aim.models import Portfolio, Holding, HoldingAlert, Transaction
from aim.forms import PortfolioForm, HoldingForm, ControlForm, TransactionForm

import logging

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context['portfolios'] = Portfolio.objects.all().count()
        context['holdings']   = Holding.objects.all().count()
        context['alerts']     = HoldingAlert.objects.all().count()

        return context

class MainView(ListView):
    """
    This is the main screen a logged in user sees for all their holdings and portfolios.
    """
    template_name = "MainView.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return Portfolio.objects.filter(owner=self.request.user).order_by("name")


# PORTFOLIO VIEWS
class PortfolioUpdate(UpdateView):
    model = Portfolio
    success_url = "/aim/"
    form_class = PortfolioForm
    template_name = "portfolio_form.html"

    def get_queryset(self):
        # return only the records that we are allowed to see
        return Portfolio.objects.filter(owner = self.request.user)

class PortfolioCreate(CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "portfolio_form.html"    

    success_url = "/aim/"

    def get_form(self, form_class=None):
        # Since we don't show the owner field, take it from the user
        # requesting to add this portfolio.
        form = super(PortfolioCreate,self).get_form(form_class)
        form.instance.owner = self.request.user

        return form

class PortfolioDelete(DeleteView):
    model = Portfolio
    template_name = "PortfolioDelete.html"
    success_url = "/aim/"
    
    def get_queryset(self):
        return Portfolio.objects.filter(owner=self.request.user)

#----------------------------------------------------------
# HOLDING VIEWS
class HoldingCreateView(CreateView):
    model = Holding
    form_class = HoldingForm
    success_url = "/aim/"
    template_name = "HoldingView.html"

    portfolio = None
    
    def get_form(self, form_class=None):
        form = super(HoldingCreateView, self).get_form(form_class)
        
        try:
            # validate that this user owns this portfolio        
            portfolio = Portfolio.objects.get(pk=self.kwargs['portid'])
            if portfolio.owner != self.request.user:
                raise ObjectDoesNotExist
        
            form.instance.portfolio = portfolio
            return form
        
        except:
            logger.exception("get_form() exception, portid= %s" % self.kwargs['portid'] )
            raise Http404
       
    
class HoldingUpdateView(UpdateView):
    template_name = "HoldingView.html"
    model = Holding
    success_url = "/aim/"
    
        
    def get_initial(self):
        # setup the symbol, otherwise it will show the FK id instead.
        initial = super(HoldingUpdateView, self).get_initial()
        initial.update( {'symbol':self.object.symbol} )
        
        return initial

    def get_queryset(self):
        # return only the records that we are allowed to see
        return Holding.objects.filter(portfolio__owner = self.request.user)

    def get_form_kwargs(self):
        kwargs = super(HoldingUpdateView,self).get_form_kwargs()

        # if we are POSTing a control button, then return the control object, 
        # otherwise treat it as a holding object.        
        if "_control" in self.request.POST:
            kwargs.update({'instance': self.object.controller})
        else:
            kwargs.update({'instance': self.object})

        return kwargs

    def get_context_data(self, **kwargs):
        cd = super(HoldingUpdateView, self).get_context_data(**kwargs)
        
        cd['controlform'] = ControlForm(instance = self.object.controller)

        return cd
    
    def get_form_class(self):
        # this line is the same as specifying the form_class as a  
        # class variable.
        if self.request.method == "GET":
            return HoldingForm
        
        # if we are posting, figure out if we hit the submit button on the holding form
        # or the control form.
        if "_holding" in self.request.POST:
            return HoldingForm
        else:
            if "_control" in self.request.POST:
                return ControlForm
            else:
                return super(HoldingUpdateView,self).get_form_class()


class HoldingDeleteView(DeleteView):
    model = Holding
    template_name = "HoldingDelete.html"
    success_url = "/aim/"
    
    def get_queryset(self):
        return Holding.objects.filter(portfolio__owner=self.request.user)


#===============================================================================
# Transaction
#===============================================================================
class TransactionCreate(CreateView):
    model = Transaction
    form_class = TransactionForm
#     success_url = "/aim/"

    type = None

#     def get_queryset(self):
#         return Transaction.objects.filter(holding__portfolio__owner = self.request.user)

    def get_form(self, form_class=None):
        form = super(TransactionCreate, self).get_form(form_class)
        holding = Holding.objects.get(pk=self.kwargs['holding_id'])

        if holding.portfolio.owner != self.request.user:
            raise

        form.instance.holding = holding

        return form

    def form_valid(self, form):
        form = super(TransactionCreate,self).form_valid(form)

        return form

    def get_initial(self):
        # we get the type of transaction from the URLconf as a named parameter.
        self.initial['type'] = self.type
        
        return super(TransactionCreate,self).get_initial()


class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = "aim/TransactionDelete.html"
    success_url = "/aim/"
    
    def get_queryset(self):
        return Transaction.objects.filter(holding__portfolio__owner=self.request.user)



