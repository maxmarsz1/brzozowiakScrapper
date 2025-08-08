from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse

from offers.models import Offer


def offers_view(request):
    object_list = Offer.objects.all()
    
    paginator = Paginator(object_list, 20)
    
    page_number = request.GET.get('page')
    
    page_obj = paginator.get_page(page_number)
        
        
    context = {
        'title': "Offers",
        'page_obj': page_obj
    }
    return render(request, "offers/offers.html", context)


def offer_view(request):
    if 'id' not in request.GET:
        return HttpResponse("Offer ID not provided", status=400)
    
    offer_id = request.GET['id']
    
    try:
        offer = Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        return HttpResponse("Offer not found", status=404)
    
    context = {
        'offer': offer
    }
    
    return render(request, 'offers/offer.html', context)