from django.core.mail import send_mail
import random
from django.conf import settings
from .models import CustomUser
from .serializers import UserRegistrationSerializer

def email_otp(email):
    CustomUser_obj = CustomUser.objects.get(email=email)
    first_name = CustomUser_obj.first_name
    last_name = CustomUser_obj.last_name
    # user=CustomUser.objects.get(first_name, last_name)
    subject = f"Store Registration"
    otp = random.randint(100000, 999999)
    message = f"Hi {first_name} {last_name},  your otp is {otp}. Do not share this OTP with anyone for security reasons. Your email is registered successfully"
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email] )
    CustomUser_obj.otp = otp
    CustomUser_obj.save()