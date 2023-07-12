from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationsFrom, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
import requests

#varification Email
from django.contrib.auth.tokens import default_token_generator   
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationsFrom(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,password=password)
            user.phone_number = phone_number
            user.save()

            # Create User PRofile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = "Please Active your account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            # messages.success(request, 'Thanks you for registration with us. We have Sent you varification email to you Plese verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationsFrom()
    
    context = {
        'form':form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Gatting Product Variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "Log In SuccessFully")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/carts/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('accounts:dashboard')
            
        else:
            messages.error(request, "Invalid login Credentials")
            return redirect("accounts:login")
    return render(request, 'accounts/login.html')

@login_required(login_url = 'accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are Loged Out")
    return redirect('accounts:login')



def accounts(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your Account Is Activated")
        return redirect('accounts:login')
    else:
        messages.error(request, "envalid activation link")
        return redirect('accounts:register')

@login_required(login_url = 'accounts:login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user, is_ordered=True)
    order_counts = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'order_counts':order_counts,
        'userprofile':userprofile,
    }
    return render(request, "accounts/dashboard.html", context)


def forgatePassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(request, "Password Reset email has been sent to your email address.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Account Does Not exist ")
            return redirect('accounts:forgatePassword')
    return render(request, 'accounts/forgatePassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Plese Resat Your Password")
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, 'This link has been Expired!')
        return redirect('accounts:login')


def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('accounts:login')
        else:
            messages.error(request, "Password do not match!")
            return redirect('accounts:resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='accounts:login')    
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        "orders":orders
    }

    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='accounts:login')
def adit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your Profile hase Been Updated")
            return redirect('accounts:adit_profile')
    else:
        user_form  = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile
    }
    return render(request, 'accounts/adit_profile.html', context)


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                
                messages.success(request, 'Password Updated Successfully')
                return redirect("accounts:change_password")
            else:
                messages.error(request, "Please Enter Valid Current Password")
                return redirect("accounts:change_password")
        else:
            messages.error(request, 'Password Does Not Match')
            return redirect("accounts:change_password")
    return render(request, "accounts/change_password.html")

@login_required(login_url='accounts:login')
def order_detailed(request, order_id) :
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = { 
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    } 
    return render(request, 'accounts/order_detailed.html', context)
