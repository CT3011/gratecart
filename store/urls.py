from django.urls import path

from . import views

app_name='store'

urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name="product_by_category"),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detailed, name="product_detailed"),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]