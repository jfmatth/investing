from django.dispatch import Signal

from loader.signals_iexcloud import LoadSymbols, LoadPricesForDay, LoadPricesForSymbol

# define the signals, and connect them
signalLoadSymbols = Signal()
signalLoadSymbols.connect(LoadSymbols)

signalLoadPricesDay = Signal()
signalLoadPricesDay.connect(LoadPricesForDay)

signalLoadPricesSymbol = Signal()
signalLoadPricesSymbol.connect(LoadPricesForSymbol)
