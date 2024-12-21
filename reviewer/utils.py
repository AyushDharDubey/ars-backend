from django.core.mail import send_mail
from django.core.cache import cache
from random import randint
from django.conf import settings
from uuid import uuid4
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone


def send_assignment_notification(user, recipent_list, assignment):
    if cache.get(user.email):
        return False
    link = ""
    subject = f"New Assignment Notification (Due in {assignment.due_date - timezone.now()})"
    message = f"""
    You have been assigned a new Assignment: {assignment.title}.
    Due Date: {assignment.due_date}.
    """
    from_email = settings.EMAIL_FROM
    # send_mail(subject, message, from_email, recipent_list)
    cache.set(user.email, 'sent', 60)
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