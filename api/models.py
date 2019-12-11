from django.db import transaction, IntegrityError
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

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create()
        if created:
            settings.rate_url = 'https://api.cryptonator.com/api/ticker/{}-{}'
            for currency_name in ['EUR', 'USD', 'GBP', 'RUB', 'BTC']:
                Currency.objects.get_or_create(name=currency_name)
            settings.main_currency = Currency.objects.first()
            settings.base_ready = True
            settings.save()
        return settings


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rate = models.DecimalField(max_digits=18, decimal_places=8, null=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user_from = models.ForeignKey(WalletUser, on_delete=models.SET_NULL, null=True, related_name='transactions')
    user_to = models.ForeignKey(WalletUser, on_delete=models.SET_NULL, null=True, related_name='transactions_to')
    amount_from = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    amount_to = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    @classmethod
    @transaction.atomic
    def make_transaction(cls, user_from, user_to, amount_from, amount_to):
        user_from.balance -= amount_from
        user_to.balance += amount_to
        user_from.save()
        user_to.save()
        if user_from.balance < 0:
            raise IntegrityError('Not enough money')
        transaction = cls.objects.create(
            user_from=user_from, user_to=user_to, amount_from=amount_from, amount_to=amount_to)
        return transaction
