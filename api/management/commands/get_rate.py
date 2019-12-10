from decimal import Decimal
from time import sleep
import requests
from django.core.management.base import BaseCommand, CommandError
from api import models

class Command(BaseCommand):
    help = 'Get currency rate every 3 minutes'

    @staticmethod
    def get_settings():
        settings, created = models.Settings.objects.get_or_create()
        if created:
            settings.rate_url = 'https://api.cryptonator.com/api/ticker/{}-{}'
            for currency_name in ['EUR', 'USD', 'GBP', 'RUB', 'BTC']:
                models.Currency.objects.get_or_create(name=currency_name)
            settings.main_currency = models.Currency.objects.first()
            settings.base_ready = True
            settings.save()
        return settings

    def handle(self, *args, **options):
        while True:
            settings = self.get_settings()
            all_rates_ok = True
            for currency in models.Currency.objects.all():
                if currency == settings.main_currency:
                    currency.rate = Decimal(1)
                    currency.save()
                else:
                    try:
                        response = requests.get(settings.rate_url.format(currency.name, settings.main_currency.name))
                        if response.json()['success']:
                            rate = Decimal(response.json()['ticker']['price'])
                        else:
                            raise Exception('Error request')
                    except Exception as e:
                        all_rates_ok = False
                        settings.last_error = str(e)
                    else:
                        currency.rate = rate
                        currency.save()
            settings.base_ready = all_rates_ok
            settings.save()
            sleep(300)
