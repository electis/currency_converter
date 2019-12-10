from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class WalletUser(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Settings(models.Model):
    main_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    base_ready = models.BooleanField(default=False)
    rate_url = models.CharField(max_length=255, default='')
    last_error = models.CharField(max_length=255, default='')


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=True)

    def __str__(self):
        return self.name