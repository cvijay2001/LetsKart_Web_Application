from django.utils import timezone
from django.shortcuts import render, redirect, reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.core.signing import SignatureExpired
from datetime import timedelta
# from django.contrib.auth.models import User

# from .forms import CustomerRegistrationForm  # Ensure your form is imported


def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    verification_link = generate_verification_link(request, user, token)
    subject = 'Verify Your Email Address'
    message = f'Click the following link to verify your email address:\n\n{verification_link}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

def generate_verification_link(request, user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Set the desired expiration time (e.g., 24 hours from now)
    expiration_time = timezone.now() + timedelta(minutes=int(settings.EMAIL_VERIFICATION_TIME_IN_MINUTES))
    
    # Create a signed URL with the token and expiration time
    signed_data = {'uidb64': uidb64, 'token': token, 'expires': expiration_time.isoformat()}
    print("signed data",signed_data)
    verification_url = request.build_absolute_uri(
        reverse('verify', kwargs={'data': signing.dumps(signed_data)})
    )
    return verification_url


# def verify(request, data):
#     try:
#         signed_data = signing.loads(data)
#         uidb64 = signed_data['uidb64']
#         token = signed_data['token']
#         print(token)
#         expiration_time_str = signed_data['expires']
#         print({"singned_data":signed_data,'uidb64':uidb64,"token":token,"expiration_time":expiration_time_str})
        
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
        
#         if user.is_active == True:
#             messages.error(request," User already verified and is Active Now")
#             return redirect(reverse('login'))


#         if not default_token_generator.check_token(user, token):
#             raise ValueError('Invalid verification link.')

#         # Extract the expiration time from the signed data
#         expiration_time = timezone.datetime.fromisoformat(expiration_time_str)
#         print('expiration_time in verify : ', expiration_time)

#         # Check if the link has expired
#         if timezone.now() > expiration_time:
#             messages.error(request, 'The verification link has expired.')
#             return redirect(reverse('login'))

#         user.is_active = True
#         user.save()
#         print("user saved email verification successfull")
#         messages.success(request, 'Your email has been verified. You can now log in.')
#         return redirect(reverse('login'))
#     except (ValueError, User.DoesNotExist, Exception) as e:
#         # print()
#         print(f'An error occurred: {e}')
#         messages.error(request,"Unexpected error occured please try again")
#         return redirect(reverse('login'))

