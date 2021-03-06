from django.urls import path
from .views import HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item_from_cart, CheckoutView, AddCouponView, ProductLandingPageView, michael, verify, category, computer, phones, accesories, search, contact_view, home


app_name = 'core'

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('', home),
    path('search/', search, name="search"),
    path('laptops/', category, name='laptops'),
    path('contact', contact_view),
    path('phones/', phones),
    path('computer/', computer),
    path('accessories/', accesories),
    path('pay', ProductLandingPageView.as_view() , name='pay'),
    path('mich/', michael),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    # path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('<str:ref>/', verify, name="verify"),     
]    