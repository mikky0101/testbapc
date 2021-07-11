from django.http import response
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
import random
import string
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.contrib.auth.models import User
from .models import Contact, Item,Order, OrderItem,  Coupon, Payment
from django.views.generic import ListView, DetailView, View, TemplateView
from django.utils import timezone
from django.shortcuts import redirect
from django.conf import settings
from jtec.settings import PAYSTACK_PUBLIC_KEY
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ContactForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm, CouponForm, PaymentForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.

def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)

def search(request):
    queryset = Item.objects.all()
    query = request.GET.get('q')
    if query:
       queryset = queryset.filter(
          Q(title__icontains=query) |
          Q(description__icontains=query)
       ).distinct()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  
    context = {
      'queryset': users
    }    
    return render(request, "templates/search.html", context)

def category(request):
    queryset = Item.objects.filter(category2="laptop")
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)        
    print(queryset)
    context = {
        'items': users
    }
    return render(request, "templates/laptops.html", context) 

def computer(request):
    queryset = Item.objects.filter(category2="computer")
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)        
    print(queryset)
    print(queryset)
    context = {
        'items': users
    }
    return render(request, "templates/computer.html", context) 

def phones(request):
    queryset = Item.objects.filter(category2="phones")
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)        
    print(queryset)
    print(queryset)
    context = {
        'items': users
    }
    return render(request, "templates/phones.html", context)     

def accesories(request):
    queryset = Item.objects.filter(category2="accessories")
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)        
    print(queryset)
    print(queryset)
    context = {
        'items': users
    }
    return render(request, "templates/accesories.html", context) 

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid    

class ProductLandingPageView(TemplateView):
    template_name = "pay.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "key": settings.PAYSTACK_PUBLIC_KEY,
            "order" : Order.objects.get(user=self.request.user, ordered=False),
            "user"  : User
        })

        return context


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "templates/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
                    return redirect("core:order-summary")       
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'templates/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")    

class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "templates/index.html"  

def home(request):
    flash = Item.objects.filter(flash=True).first()
    top = Item.objects.filter(flash=True).last()
    item = Item.objects.all()
    context = {
        "flash": flash,
        "top": top,
        "item": item
    }
    return render(request, "templates/index.html", context)     

class ItemDetailView(DetailView):
    model = Item
    template_name = "templates/product2.html"

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
        

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")

def contact_view(request: HttpRequest) -> HttpResponse:
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            street_address = form.cleaned_data["street_address"]
            apartment_address = form.cleaned_data["apartment_address"]
            phone_number2 = form.cleaned_data["phone_number2"]
            phone_number = form.cleaned_data["phone_number"]
            state = form.cleaned_data["state"]
            Contact.objects.create(user=request.user, street_address=street_address, apartment_address=apartment_address, phone_number=phone_number, phone_number2=phone_number2, state=state)
            return redirect("/")
    context = {
        "form": form
    }        
    return render(request, "templates/address.html", context)



def michael(request: HttpRequest) -> HttpResponse:
    form = PaymentForm()
    if request.method == "POST":
        form = PaymentForm(request.POST)
        order = Order.objects.get(user=request.user, ordered=False)
        if form.is_valid():
            email = form.cleaned_data["email"]
            amount = order.get_total()
            order = Order.objects.get(user=request.user)
            Payment.objects.create(
                amount= amount,
                email = email,
                order = order
            )
            payment = Payment.objects.filter(amount=order.get_total()).last()
            return render(request, "templates/initiate.html", {"payment": payment, "paystack_public_key": PAYSTACK_PUBLIC_KEY})
    context = {
        "form": form,
        "order": Order.objects.get(user=request.user, ordered=False)
    }             
    return render(request, "templates/mike.html", context)

def verify(request: HttpRequest, ref: str) -> HttpResponse:
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, "succesful transaction")
    return redirect('core:home')      