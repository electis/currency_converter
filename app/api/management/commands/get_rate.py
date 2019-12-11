from decimal import Decimal
from time import sleep
import requests
from django.core.management.base import BaseCommand
from api import models

class Command(BaseCommand):
    help = 'Get currency rate every 3 minutes'

    def handle(self, *args, **options):
        while True:
            settings = models.Settings.get_settings()
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
                            raise Exception(response.json()['error'])
                    except Exception as e:
                        all_rates_ok = False
                        settings.last_error = str(e)
                        break
                    else:
                        currency.rate = rate
                        currency.save()
            settings.base_ready = all_rates_ok
            settings.save()
            sleep(300)
