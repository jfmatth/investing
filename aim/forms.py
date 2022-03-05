from django import forms
from django.core.exceptions import ObjectDoesNotExist

from aim.models import Portfolio, Holding, AimController, Transaction, Symbol

import logging

logger = logging.getLogger(__name__)

class ControlForm(forms.ModelForm):
    class Meta:
        model = AimController
        fields = ('started',
                  'control',
                  'sellsafe',
                  'buysafe', 
                  'buymin',
                  'sellmin',
                  'buyperc', 
                  'sellperc',
                  )
       


class PortfolioForm(forms.ModelForm):
    user = None
    
    class Meta:
        model = Portfolio
        exclude = ('owner',)
    
    def clean(self):
        # validate that this portfolio for this user doesn't already exist.
        try:
            Portfolio.objects.get(name=self.cleaned_data['name'], owner=self.instance.owner)
        except ObjectDoesNotExist:
            # record not found, OK.
            pass
        else:
            # no exception, meaning duplicate.
            logger.exception("Portfolioform - duplicate Name")
            raise forms.ValidationError('Portfolio with this Name already exists')
        
        return super(PortfolioForm,self).clean()


class HoldingForm(forms.ModelForm):
    # define symbol here to override the default ModelChoicefield dropdown list.
    symbol = forms.CharField()

    def clean_symbol(self):
        # Since symbol needs to be a symbol object, use the clean
        # method to make sure it's valid, and if it is, return a symbol object, not the text.
        try:
            return Symbol.objects.get(name__iexact=self.cleaned_data['symbol'])
        except ObjectDoesNotExist:
            logger.exception("HoldingForm - Invalid symbol")
            raise forms.ValidationError("Invalid symbol")

    def clean(self):
        clean_data = super(HoldingForm, self).clean()
        
        try:
            Holding.objects.get(symbol=clean_data['symbol'], portfolio=self.instance.portfolio)
        except:
            pass
        else:
            logger.exception("HoldingForm - Duplicate symbol in portfolio")
            raise forms.ValidationError("Duplicate symbol")
 
        return super(HoldingForm, self).clean()
    
    class Meta:
        model = Holding
        fields = ('symbol', 'reason' )


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransactionForm,self).__init__(*args, **kwargs)

#         # The holding field is for display only, and convenience, but they can't change it.
#         self.fields['holding'].initial = self.initial['holding_id']
#         self.fields['holding'].required = False
#         self.fields['holding'].widget.attrs['disabled'] = True
      
        # Same thing with the type of transaction we are doing.
        self.fields['type'].required = True
        self.fields['type'].widget.attrs['disabled'] = False
      
        
#     def clean_holding(self):
#         # since we have it disabled, we need to put it back to something as 'clean'
#         print "cleaned holding %s" % self.cleaned_data['holding']
#         return Holding.objects.get(id=self.initial['holding_id'])
    
    def clean_type(self):
        # disabled fields need clean values.
        return self.initial['type']
        
    class Meta:
        model = Transaction
#         fields = ('date', 'shares', 'price', 'holding', 'type' )
        fields = ('date', 'shares', 'price', 'type' )

