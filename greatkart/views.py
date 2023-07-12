from django.shortcuts import render

from store.models import Product, ReviewRating

def home(request):
    product = Product.objects.all().filter(is_avalable=True).order_by('created_date')

    # Get All Reviews
    for products in product:
        reviews = ReviewRating.objects.filter(product_id=products.id, status=True)
    context = {
        'products'  : product,
        'reviews'   : reviews,
    }
    return render(request, 'home.html', context)