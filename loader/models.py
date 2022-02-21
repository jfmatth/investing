from django.db import models

# Create your models here.
class BaseModel(models.Model):
    '''
    Defines some of the base models common fields and functions, mainly save() so we can
    track when the record was updated or created.
    
    Might be worth checking out https://github.com/WiserTogether/django-base-model

    '''
    cdate = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Date Created")     
    mdate = models.DateTimeField(auto_now=True, null=True, verbose_name="Date Modified")
    
    class Meta:
        abstract = True

class Exchange(BaseModel):
    name = models.CharField(max_length=100, db_index=True)
    data = models.TextField(blank=True, null=True)
    
    loaded = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s" % (self.name) 

class ExchangePrice(BaseModel):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    data = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    loaded = models.BooleanField(default=False)
    
class PriceError(BaseModel):
    symbolname = models.CharField(max_length=10, db_index=True, unique=True)
    
    def __str__(self):
        return self.symbolname

class ExchangeSplit(BaseModel):
   exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
   data = models.TextField(blank=True, null=True)
   date = models.DateField(blank=True, null=True)
   loaded = models.BooleanField(default=False)
