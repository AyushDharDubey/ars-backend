from django.core.mail import send_mail
from django.core.cache import cache
from random import randint
from django.conf import settings
from uuid import uuid4
from django.contrib.auth.tokens import default_token_generator
import os


def send_account_activation(user):
    if cache.get(user.email):
        return False
    otp = randint(100000, 999999)
    email_verification_token = uuid4()
    # link = ""
    # subject = ""
    # message = ""
    # from_email = settings.EMAIL_FROM
    # recipient_list = [user.email, ]
    # send_mail(subject, message, from_email, recipient_list)
    cache.set(user.email, otp, 60)
    user.otp = otp
    user.email_verification_token = email_verification_token
    user.save()
    return True

def send_password_reset(user):
    if cache.get(user.email):
        return False
    token = default_token_generator.make_token(user)
    # link = ''
    # subject = ""
    # message = f""""""
    # from_email = settings.EMAIL_FROM
    # recipient_list = [user.email, ]
    # print(send_mail(subject, message, from_email, recipient_list))
    cache.set(user.email, token, 60)
    return True