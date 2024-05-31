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
from datetime import timedelta
from .helpers.email_verification import send_verification_email
from django.template.loader import render_to_string
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

# class CustomerRegistrationView(View):
#  def get(self,request):
#   form = CustomerRegistrationForm()
#   return render(request,'app/customerregistration.html',{'form':form})

#  def post(self,request):
#   form = CustomerRegistrationForm(request.POST)
#   if form.is_valid():
#    form.save()
#    messages.success(request,'Congratulations! Registration Successfully')
#    return redirect(reverse('login'))
#   return render(request,'app/customerregistration.html',{'form':form})

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
    


# views.py
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime


def current_time_view(request):
    current_time = (timezone.now())
    return HttpResponse(f"The current server time is: {current_time}")

from django.views import View
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing
from django.core.signing import SignatureExpired
from .forms import CustomerRegistrationForm  # Ensure your form is imported

class CustomerRegistrationView(View):
  def get(self, request):
      form = CustomerRegistrationForm()
      return render(request, 'app/customerregistration.html', {'form': form})

  def post(self, request):
    form = CustomerRegistrationForm(request.POST)
    print("in cust registration before form is valid")
    if form.is_valid():
      print("in cust registration After form is valid")

        # Create user but don't save yet
      user = form.save(commit=False)
        
      user.is_active = False  # Mark user as inactive until email is verified
      
      user.save()
      print(user.pk)

      send_verification_email(request,user)

      messages.success(request, 'Please check your email to verify your account.')
      return redirect(reverse('login'))
    return render(request, 'app/customerregistration.html', {'form': form})
    
  
#   def send_verification_email(self, request, user):
#     token = default_token_generator.make_token(user)
#     verification_link = self.generate_verification_link(request, user, token)
#     subject = 'Verify Your Email Address'
#     message = f'Click the following link to verify your email address:\n\n{verification_link}'
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

#   def generate_verification_link(self, request, user, token):
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
#     # Set the desired expiration time (e.g., 24 hours from now)
#     expiration_time = timezone.now() + timedelta(minutes=1)
    
#     # Create a signed URL with the token and expiration time
#     signed_data = {'uidb64': uidb64, 'token': token, 'expires': expiration_time.isoformat()}
#     print("signed data",signed_data)
#     verification_url = request.build_absolute_uri(
#         reverse('verify', kwargs={'data': signing.dumps(signed_data)})
#     )

#     print("verffiation_url",verification_url)
    
#     return verification_url



def verify(request, data):
    try:
        signed_data = signing.loads(data)
        uidb64 = signed_data['uidb64']
        token = signed_data['token']
        print(token)
        expiration_time_str = signed_data['expires']
        print({"singned_data":signed_data,'uidb64':uidb64,"token":token,"expiration_time":expiration_time_str})
        
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if user.is_active == True:
          messages.error(request," User already verified and is Active Now")
          return redirect(reverse('login'))

        if not default_token_generator.check_token(user, token):
          raise ValueError('Invalid verification link.')

        # Extract the expiration time from the signed data
        expiration_time = timezone.datetime.fromisoformat(expiration_time_str)
        print('expiration_time in verify : ', expiration_time)

        # Check if the link has expired
        if timezone.now() > expiration_time:
            messages.error(request, 'The verification link has expired.')
            return redirect(reverse('login'))

        user.is_active = True
        user.save()
        print("user saved email verification successfull")
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect(reverse('login'))
    except (ValueError, User.DoesNotExist, Exception) as e:
        # print()
        print(f'An error occurred: {e}')
        messages.error(request,"Unexpected error occured please try again")
        return redirect(reverse('login'))




from .forms  import LoginForm
from django.contrib.auth.views import LoginView
class CustomLoginView(LoginView):

    authentication_form = LoginForm

    def form_invalid(self, form):
        username = form.data.get('username')
        user = User.objects.filter(username=username).first()
        print(user )

        if user and not user.is_active:
          send_verification_email(request=self.request,user=user)

            # self.send_verification_email(self.request, user)
          messages.error(self.request, 'Your account is not active. Please verify your email.')
          return redirect(reverse('login'))

        return super().form_invalid(form)

    # def send_verification_email(self, request, user):
    #     token = default_token_generator.make_token(user)
    #     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    #     verification_link = request.build_absolute_uri(reverse('verify', kwargs={'uidb64': uidb64, 'token': token}))
        
    #     subject = 'Verify Your Email Address'
    #     message = render_to_string('app/verification_email.html', {
    #         'user': user,
    #         'verification_link': verification_link,
    #     })
    #     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])