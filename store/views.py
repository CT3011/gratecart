from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from category.models import Category
from carts.models import Cart, CartItem
from orders.models import OrderProduct
from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm

from carts.views import _cart_id
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_avalable = True)
        pagenator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = pagenator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_avalable=True).order_by('id')
        pagenator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = pagenator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        "product_count": product_count,
    }
    return render(request, 'store/store.html', context)

def product_detailed(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    # Get All Reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # get PRoduct Galary
    product_galary = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product'    : single_product,
        "in_cart"           : in_cart,
        'orderproduct'      : orderproduct,
        'reviews'           : reviews,
        'product_galary'    : product_galary,

    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(discription__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
        context = {}
        try:
            context = {
                'products': products,
                "product_count": product_count,
            }
        except:
            pass
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Thank You Youser review is been Updated")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save() 
                messages.success(request, "Thank You Youser review is been Submited")
                return redirect(url)


