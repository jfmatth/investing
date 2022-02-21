from logging import log
from django.urls import path
from django.contrib.auth.decorators import login_required

from aim.views import HoldingCreateView, HoldingDeleteView, MainView, PortfolioUpdate, PortfolioCreate, PortfolioDelete, HoldingUpdateView
from aim.views import TransactionCreate, TransactionDeleteView 

urlpatterns = [
    
    # main /AIM URL
    path('', login_required(MainView.as_view() ) , name='aim_main'), 

    # Portfolio URL's

    # url(r'^portfolio/(?P<pk>\d+)/$',
    #     login_required(PortfolioUpdate.as_view()),
    #     name = "portfolio_edit" ),
    path('portfolio/<int:pk>', login_required( PortfolioUpdate.as_view() ), name="portfolio_edit" ),
    
    # url(r'^portfolio/add/$',
    #     login_required(PortfolioCreate.as_view()),
    #     name = "portfolio_add" ),
    path('portfolio/add/', login_required( PortfolioCreate.as_view() ), name="portfolio_add"), 

    # url(r'^portfolio/delete/(?P<pk>\d+)/$',
    #     login_required(PortfolioDelete.as_view()),
    #     name = "portfolio_delete"),
    path('portfolio/delete/<int:pk>', login_required( PortfolioDelete.as_view() ), name="portfolio_delete"), 


    # Holding URL's

    # url(r'^holding/add/(?P<portid>\d+)/$',
    #     login_required(HoldingCreateView.as_view()),
    #     name = "holding_add"),
    path('holding/add/<int:portid>/', login_required( HoldingCreateView.as_view() ), name="holding_add"),

    # url(r'^holding/add/$',
    #     login_required(HoldingCreateView.as_view()),
    #     name = "holding_addplain"),
    path('holding/add/', login_required( HoldingCreateView.as_view() ), name="holding_addplain"),

    # url(r'^holding/(?P<pk>\d+)/$',
    #     login_required(HoldingUpdateView.as_view()),
    #     name = "holding_view"),
    path('holding/<int:pk>', login_required( HoldingUpdateView.as_view()), name="holding_view" ),
    

    # url(r'^holding/delete/(?P<pk>\d+)/$',
    #     login_required(HoldingDeleteView.as_view()),
    #     name = "holding_delete"),
    path('holding/delete/<int:pk>',login_required( HoldingDeleteView.as_view() ), name="holding_delete"),


    # Transaction URL's
    # url(r'^transaction/(?P<holding_id>\d+)/buy/$',
    #     login_required(TransactionCreate.as_view(type="Buy") ),
    #     name = "transaction_buy"),
    path('transaction/<int:holding_id>/buy', login_required(TransactionCreate.as_view() ), name="transaction_buy"),
                       
    # url(r'^transaction/(?P<holding_id>\d+)/sell/$',
    #     login_required(TransactionCreate.as_view(type="Sell") ),
    #     name = "transaction_sell"),
    path('transaction/<int:holding_id>/sell', login_required(TransactionCreate.as_view() ), name="transaction_sell"),

    # url(r'^transaction/delete/(?P<pk>\d+)/$',
    #     login_required(TransactionDeleteView.as_view()),
    #     name="transaction_delete"),
    path('transaction/delete/<int:pk>', login_required(TransactionDeleteView.as_view() ), name = "transaction_delete"),
    
    # url(r'amiok/$',
    #     TemplateView.as_view(template_name="aim/amiok.html")
    #     ),





]