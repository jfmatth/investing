# module to recieve signals and execute the code

from django.dispatch import receiver, Signal

# define the signal
signalLoadSymbols = Signal()

@receiver(signalLoadSymbols)
def receiverLoadSymbols(sender, **kwargs):
    print("received signal")

