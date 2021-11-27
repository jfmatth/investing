# module to recieve signals and execute the code

from django.dispatch import Signal

from loader.loader_iexcloud import receiverLoadSymbols

# define the signal, and connect it
signalLoadSymbols = Signal()
signalLoadSymbols.connect(receiverLoadSymbols)
