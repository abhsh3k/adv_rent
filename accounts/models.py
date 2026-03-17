import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('renter', 'Renter'),
        ('owner', 'Owner'),
        ('both', 'Both'),
    ]

    role               = models.CharField(max_length=10, choices=ROLE_CHOICES, default='renter')
    phone              = models.CharField(max_length=15, blank=True)
    bio                = models.TextField(blank=True)
    avatar             = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # contact verification
    email_verified     = models.BooleanField(default=False)
    phone_verified     = models.BooleanField(default=False)
    is_active          = models.BooleanField(default=False)  # inactive until OTP verified

    # ID verification
    is_verified        = models.BooleanField(default=False)
    id_document        = models.ImageField(upload_to='id_docs/', blank=True, null=True)
    terms_accepted     = models.BooleanField(default=False)

    # OTP fields
    otp_code           = models.CharField(max_length=6, blank=True)
    otp_expires_at     = models.DateTimeField(null=True, blank=True)
    otp_method         = models.CharField(max_length=10, blank=True)  # 'email' or 'phone'

    # telegram
    telegram_chat_id    = models.CharField(max_length=20, blank=True)
    telegram_username   = models.CharField(max_length=50, blank=True)
    telegram_link_token = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_contact_verified(self):
        return self.email_verified or self.phone_verified