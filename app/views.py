from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .forms import (CustomerRegistrationForm,CustomerProfileForm, MyPasswordChangeForm)
from django.views import View
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView
from .models import (Customer,
                     Product,
                     Cart,
                     OrderPlaced)
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
# def home(request):
#  return render(request, 'app/home.html')


def cart_count(request): # NO url associated with this 
 cartcount = Cart.objects.filter(user=request.user).count()
 return cartcount

class ProductView(View):
 def get(self,request):
  topwears = Product.objects.filter(category = 'TW')
  bottomwears = Product.objects.filter(category = 'BW')
  mobiles = Product.objects.filter(category = 'M')
  laptops = Product.objects.filter(category='L')
  if request.user.is_authenticated:
   cartcount = cart_count(request)
  else:
   cartcount = ''
   
  return render(request,'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'laptops':laptops,'cartcount':cartcount})

# def product_detail(request):
#  return render(request, 'app/productdetail.html')
 
class ProductDetailView(View):
 def get(self,request,pk):
  if request.user.is_authenticated:
   cartcount = cart_count(request)
  else:
   cartcount = ''
  product = Product.objects.get(pk=pk)
  prod_already_in_cart = Cart.objects.filter(Q(product = product) & Q(user=request.user.id)).exists()
  # prod_already_in_cart = Cart.objects.filter(user=request.user,product = product)
 
  
  return render(request,'app/productdetail.html',{'product':product,'prod_already_in_cart':prod_already_in_cart,'cartcount':cartcount})
 
@login_required()
def add_to_cart(request):
  user = request.user
  product_id = request.GET.get('prod-id',None)
  if product_id:
    product_instance = Product.objects.get(id = product_id)
    cart_item = Cart.objects.filter(user = user, product = product_instance)
    
    if cart_item.exists():
      return redirect(reverse('showcart'))
    else:
      Cart(user = user, product=product_instance).save()
      messages.info(request, 'Product Added into Cart.')
    return redirect(reverse('showcart'))
  else:
   return redirect(reverse('home'))

# def add_to_cart_optional(request):
#     user = request.user
#     product_id = request.GET.get('prod-id')
#     product_instance = get_object_or_404(Product, id=product_id)
#     cart_item, created = Cart.objects.update_or_create(
#         user=user,
#         product=product_instance,
#         defaults={'quantity': 1},
#     )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     return redirect(reverse('showcart'))
@login_required()
def show_cart(request):
  user = request.user
  cart_obj = Cart.objects.filter(user=user)
  amount = 0.0
  shipping_amount = 70.0
  # cart_product = [p for p in Cart.objects.all() if p.user == user ]
  cart_product = [p for p in Cart.objects.all() if p.user == user ]
  if cart_product:
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount += tempamount
      totalamount = amount + shipping_amount
    return render(request, 'app/addtocart.html',{'carts':cart_obj, 'totalamount': totalamount,'amount': amount,'cartcount':cart_count(request)}) 
  else:
    return render(request,'app/emptycart.html',{'cartcount':cart_count(request)})
 
def plus_cart(request):
 if request.method == 'GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) & Q(user= request.user))
  c.quantity+=1
  c.save()
  amount = 0
  shipping_amount = 70.0
  cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
  if cart_product:
   for p in cart_product:
    tempamount = (p.quantity * p.product.discounted_price)
    amount += tempamount
 

  data = {
   'quantity':c.quantity,
   'amount':amount,
   'totalamount':amount + shipping_amount
  }
  return JsonResponse(data)
 
def minus_cart(request):
 if request.method == 'GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) & Q(user= request.user))

  if c.quantity > 1:
    c.quantity -= 1
    c.save()

  amount = 0
  shipping_amount = 70.0
  cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
  if cart_product:
   for p in cart_product:
    tempamount = (p.quantity * p.product.discounted_price)
    amount += tempamount

  data = {
   'quantity':c.quantity,
   'amount':amount,
   'totalamount':amount + shipping_amount
  }
  return JsonResponse(data)

def remove_cart(request):
 if request.method == 'GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) & Q(user= request.user))
  c.delete()

  amount = 0
  shipping_amount = 70.0
  cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
  if cart_product:
   for p in cart_product:
    tempamount = (p.quantity * p.product.discounted_price)
    amount += tempamount

  data = {
   'quantity':c.quantity,
   'amount':amount,
   'totalamount':amount + shipping_amount,
   'cartcount':cart_count(request)
  }
  return JsonResponse(data) 
 
  
def buy_now(request):
 return render(request, 'app/buynow.html')

# def profile(request):
#  return render(request, 'app/profile.html')
@login_required()
def address(request):
 add = Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html',{'add':add, 'active':'btn-primary','cartcount':cart_count(request)})

@login_required()
def orders(request):
 op = OrderPlaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html',{'orderplaced':op,'cartcount':cart_count(request)})

# @login_required()
# def change_password(request):
#  cartcount = cart_count(request)
#  print('-------------',cartcount)
#  return render(request, 'app/changepassword.html',{'cartcount':cartcount})

def  mobile(request,data = None):
 if request.user.is_authenticated:
  cartcount = cart_count(request)
 else:
  cartcount = ''
 if data == None:
  mobiles = Product.objects.filter(category='M')
 elif data in ('Samsung','Redmi','IQOO','Iphone','OnePlus'):
  mobiles = Product.objects.filter(category='M').filter(brand = data) 
 elif data == 'below_10k':
  mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
 elif data == 'above_10k':
  mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)

 return render(request, 'app/mobile.html',{'mobiles':mobiles,'cartcount':cartcount})

def laptop(request,data = None):
 if request.user.is_authenticated:
  cartcount = cart_count(request)
 else:
  cartcount = ''
   
 if data == None:
  laptops = Product.objects.filter(category='L')
 elif data in ('ASUS','HP','Dell','MSI'):
  laptops = Product.objects.filter(category='L').filter(brand = data) 
 elif data == 'below_40k':
  laptops = Product.objects.filter(category='L').filter(discounted_price__lt=40000)
 elif data == 'above_40k':
  laptops = Product.objects.filter(category='L').filter(discounted_price__gt=40000)

 return render(request, 'app/laptop.html',{'laptops':laptops,'cartcount':cartcount})

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
 def get(self,request):
  form = CustomerRegistrationForm()
  return render(request,'app/customerregistration.html',{'form':form})

 def post(self,request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   form.save()
   messages.success(request,'Congratulations! Registration Successfully')
   return redirect(reverse('login'))
  return render(request,'app/customerregistration.html',{'form':form})

@login_required()
def checkout(request):
 user = request.user
 address = Customer.objects.filter(user = user)
 cart_items = Cart.objects.filter(user = user)
 amount = 0
 shipping_amount = 70.0
 total_amount = 0.0
 cart_product = [p for p in Cart.objects.all() if p.user == request.user ]

 if cart_product:
  for p in cart_product:
   temp_amount = (p.quantity * p.product.discounted_price)
   amount += temp_amount
  total_amount = amount + shipping_amount
 return render(request, 'app/checkout.html',{'address':address,'total_amount':total_amount,'cart_items':cart_items,'cartcount':cart_count(request)    })

@login_required()
def payment_done(request):
 if request.method == "GET":
  user = request.user
  custid= request.GET.get('custid',None)
  if custid:
    customer = Customer.objects.get(id=custid)
    cart_items = Cart.objects.filter(user=user)
    for c in cart_items:
      order_placed = OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity)
      order_placed.save()
      c.delete()
  return redirect(reverse('orders'))


class ProfileView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next' 

    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary','cartcount':cart_count(request)})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        form.instance.user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, 'Congratulations!!! Address Saved Successfully')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary','cartcount':cart_count(request)})



class MyPasswordChangeView(PasswordChangeView):
    template_name = 'app/passwordchange.html'
    form_class = MyPasswordChangeForm
    success_url = '/passwordchangedone/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cartcount'] = cart_count(self.request)
        return context
class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'app/passwordchangedone.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cartcount'] = cart_count(self.request)
        return context
    
    
  


