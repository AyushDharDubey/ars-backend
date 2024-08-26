from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username = username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    REGISTRATION_CHOICES = [
        ("email", "Email"),
        ("channel i", "Channel I"),
    ]
    registration_method = models.CharField(
        _("registration method"),
        max_length=10,
        choices=REGISTRATION_CHOICES,
        default="email",
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    otp = models.CharField(
        _("otp"),
        max_length=6,
        null=True,
        blank=True,
    )
    email_verification_token = models.CharField(
        _("email verification token"),
        max_length=248,
        null=True,
        blank=True,
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_permissions",
        related_query_name="user",
    )
    REQUIRED_FIELDS=["email", "first_name", "last_name"]