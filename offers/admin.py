from django.contrib import admin
from offers.models import Offer, OfferFailed

# Register your models here.


admin.site.register(Offer)
admin.site.register(OfferFailed)